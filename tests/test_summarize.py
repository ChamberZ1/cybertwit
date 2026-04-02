import unittest
from unittest.mock import Mock, patch

import summarize


class SummarizeTests(unittest.TestCase):
    def test_format_summaries_includes_source_when_present(self):
        items = [
            {"title": "Alert on active exploitation", "source": "CISA"},
            {"title": "Patch release available", "source": ""},
        ]

        result = summarize.format_summaries(items)

        self.assertEqual(
            result,
            "- Alert on active exploitation (CISA)\n- Patch release available",
        )

    def test_summarize_with_groq_posts_openai_compatible_payload(self):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Ranked digest"}}
            ]
        }

        with patch.object(summarize, "GROQ_API_KEY", "test-key"), patch.object(
            summarize, "GROQ_MODEL_NAME", "llama-3.1-8b-instant"
        ), patch("summarize.requests.post", return_value=mock_response) as mock_post:
            result = summarize.summarize_with_groq("prompt text")

        self.assertEqual(result, "Ranked digest")
        mock_post.assert_called_once()

        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(
            kwargs["json"]["model"],
            "llama-3.1-8b-instant",
        )
        self.assertEqual(
            kwargs["json"]["messages"],
            [
                {"role": "system", "content": "You are a cybersecurity news analyst."},
                {"role": "user", "content": "prompt text"},
            ],
        )
        self.assertEqual(kwargs["json"]["temperature"], 0.2)

    def test_ai_daily_digest_falls_back_to_groq_when_gemini_fails(self):
        items = [
            {
                "title": "Researchers find phishing browser issue",
                "summary": "A browser assistant was coaxed into leaking credentials.",
                "source": "The Hacker News",
                "link": "https://example.com/story",
            }
        ]

        with patch.object(summarize, "client", object()), patch(
            "summarize.summarize_with_gemini",
            side_effect=RuntimeError("Gemini overloaded"),
        ), patch("summarize.time.sleep", return_value=None), patch.object(
            summarize, "GROQ_API_KEY", "test-key"
        ), patch(
            "summarize.summarize_with_groq",
            return_value="Phishing risk highlighted\nhttps://example.com/story",
        ) as groq_mock:
            result = summarize.ai_daily_digest(items)

        self.assertIn("Phishing risk highlighted", result)
        groq_mock.assert_called_once()

    def test_summarize_with_groq_raises_response_details_on_http_error(self):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.reason = "Bad Request"
        mock_response.text = '{"error":{"message":"model is required"}}'

        with patch.object(summarize, "GROQ_API_KEY", "test-key"), patch(
            "summarize.requests.post", return_value=mock_response
        ):
            with self.assertRaisesRegex(
                Exception, '400 Bad Request: {"error":{"message":"model is required"}}'
            ):
                summarize.summarize_with_groq("prompt text")


if __name__ == "__main__":
    unittest.main()
