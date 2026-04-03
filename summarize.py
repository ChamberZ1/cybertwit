import logging
from typing import List, Dict
from dotenv import load_dotenv
import os
import time
import requests
from google import genai
from google.genai import types

load_dotenv()  # Load environment variables from .env file if present
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API")
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
DEFAULT_GEMINI_MODEL_NAME = "gemini-3-flash-preview"
DEFAULT_GROQ_MODEL_NAME = "llama-3.1-8b-instant"
OPEN_ROUTER_MODEL = "openrouter/free"  # auto-routes to best available free model

client = genai.Client(api_key=GEMINI_API_KEY, http_options=types.HttpOptions(timeout=30000)) if GEMINI_API_KEY else None
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", DEFAULT_GEMINI_MODEL_NAME)
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", DEFAULT_GROQ_MODEL_NAME)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
OPEN_ROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def build_news_block(items: List[Dict]) -> str:
    blocks = []
    for item in items:
        title = item.get("title", "").strip()
        summary = item.get("summary", "").strip()
        source = item.get("source", "").strip()
        link = item.get("link", "").strip()

        if not title:
            continue

        block = f"- {title}"
        if summary:
            block += f": {summary}"
        if source:
            block += f" ({source})"
        if link:
            block += f" ({link})"

        blocks.append(block)

    return "\n".join(blocks)

def build_digest_prompt(items: List[Dict]) -> str:
    news_block = build_news_block(items)

    return f"""
You are a cybersecurity news analyst.

Given the following list of cybersecurity news items, produce a ranked list of cybersecurity summaries for posting on X.

Rules:
- Rank by defender relevance — most critical first
- One bullet per news item, followed by the link on the next line
- Each bullet + link pair must be under 280 characters total
- Lead with a strong noun or action verb
- Active voice, no emojis, no hashtags, no em-dashes, no marketing language, no "facilitate"
- Blank line between each bullet+link pair
- Assume a technical audience (SOC analysts, pentesters, security engineers)

News items:
{news_block}
"""

def summarize_with_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt
    )
    return (response.text or "").strip()

def summarize_with_groq(prompt: str) -> str:
    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL_NAME,
            "messages": [
                {"role": "system", "content": "You are a cybersecurity news analyst."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason}: {response.text}",
            response=response,
        )
    data = response.json()
    return (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )

def summarize_with_open_router(prompt: str) -> str:
    response = requests.post(
        OPEN_ROUTER_API_URL,
        headers={
            "Authorization": f"Bearer {OPEN_ROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPEN_ROUTER_MODEL,
            "messages": [
                {"role": "system", "content": "You are a cybersecurity news analyst."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason}: {response.text}",
            response=response,
        )
    data = response.json()
    return (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )

def ai_daily_digest(items: List[Dict]) -> str:
    if not items:
        return ""

    prompt = build_digest_prompt(items)
    delays = [6, 9]  # first REtry has 6s delay, second has 9s delay, total 3 tries.

    if client:
        for attempt in range(3):
            try:
                summary = summarize_with_gemini(prompt)
                if summary:
                    return summary
            except Exception as e:
                logging.warning(f"Gemini attempt {attempt+1}/3 failed: {e}")
                if attempt < 2:
                    logging.info(f"Retrying Gemini in {delays[attempt]}s...")
                    time.sleep(delays[attempt])

    if GROQ_API_KEY:
        for attempt in range(3):
            try:
                summary = summarize_with_groq(prompt)
                if summary:
                    return summary
            except Exception as e:
                logging.warning(f"Groq attempt {attempt+1}/3 failed: {e}")
                if attempt < 2:
                    logging.info(f"Retrying Groq in {delays[attempt]}s...")
                    time.sleep(delays[attempt])

    if OPEN_ROUTER_API_KEY:
        try:
            summary = summarize_with_open_router(prompt)
            if summary:
                return summary
        except Exception as e:
            logging.warning(f"OpenRouter summarization failed: {e}")

    logging.error("AI summarization failed: Gemini, Groq, and OpenRouter were unavailable.")
    return ""



def format_summaries(items: List[Dict[str, str]]) -> str:
    """
    Given a list of dicts with 'title' and 'source', return lines like:
    • Title (Source)
    """
    lines = []
    for item in items:
        title = (item.get("title") or "").strip()
        source = (item.get("source") or "").strip()
        if not title:
            continue
        if source:
            lines.append(f"- {title} ({source})")
        else:
            lines.append(f"- {title}")
    return "\n".join(lines)

# for testing
if __name__ == "__main__":
    data = [
        {
            "title": "Ivanti warns of two EPMM flaws exploited in zero-day attacks",
            "link": "https://www.bleepingcomputer.com/news/security/ivanti-warns-of-two-epmm-flaws-exploited-in-zero-day-attacks/",
            "summary": "Ivanti has disclosed two critical vulnerabilities in its Endpoint Manager Mobile product that are actively exploited in the wild.",
            "published": "2026-01-31T10:15:00Z",
            "source": "BleepingComputer",
        },
        {
            "title": "Google patches actively exploited Chrome vulnerability",
            "link": "https://security.googleblog.com/2026/01/google-patches-chrome-vulnerability.html",
            "summary": "Google released an emergency update to address a high-severity Chrome zero-day vulnerability exploited in targeted attacks.",
            "published": "2026-01-31T08:42:00Z",
            "source": "Google Security Blog",
        },
        {
            "title": "Ransomware gang targets healthcare providers across Europe",
            "link": "https://thehackernews.com/2026/01/ransomware-healthcare-europe.html",
            "summary": "A new ransomware campaign has been observed targeting hospitals and healthcare organizations across multiple European countries.",
            "published": "2026-01-31T06:30:00Z",
            "source": "The Hacker News",
        },
        {
            "title": "CISA adds actively exploited vulnerability to KEV catalog",
            "link": "https://www.cisa.gov/news-events/alerts/2026/01/cisa-adds-vulnerability",
            "summary": "CISA has added a newly disclosed vulnerability to its Known Exploited Vulnerabilities catalog and urges immediate patching.",
            "published": "2026-01-31T05:10:00Z",
            "source": "CISA",
        },
    ]
    print(format_summaries(data))
