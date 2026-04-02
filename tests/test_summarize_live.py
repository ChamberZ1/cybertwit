import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import summarize


class GroqLiveTests(unittest.TestCase):
    def setUp(self):
        if os.getenv("RUN_LIVE_GROQ_TESTS") != "1":
            self.skipTest("Set RUN_LIVE_GROQ_TESTS=1 to run live Groq tests.")

    def test_groq_api_key_is_configured(self):
        self.assertTrue(
            summarize.GROQ_API_KEY,
            "GROQ_API or GROQ_API_KEY is not set.",
        )
        self.assertTrue(
            summarize.GROQ_MODEL_NAME,
            "GROQ_MODEL_NAME is not set.",
        )

    def test_groq_live_request_succeeds(self):
        prompt = (
            "Reply with exactly one bullet under 20 words about defenders patching a "
            "critical vulnerability."
        )

        result = summarize.summarize_with_groq(prompt)

        self.assertTrue(result, "Groq returned an empty response.")
        self.assertRegex(
            result,
            r"^\s*[-*•]\s+",
            "Expected a bullet-style response from Groq.",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
