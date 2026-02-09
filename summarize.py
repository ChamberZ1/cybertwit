import sys
import json
from typing import List, Dict
from dotenv import load_dotenv
import os
from google import genai
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3-flash-preview"  

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

def ai_daily_digest(items: List[Dict]) -> str:
    if not items:
        return ""

    news_block = build_news_block(items)

    prompt = f"""
You are a cybersecurity news analyst.

Given the following list of cybersecurity news items, produce a concise daily digest.

Rules:
- Rank the news items by importance to defenders and security practitioners, with the most critical at the top. 
- One bullet point for each news item
- Each bullet should be 2-3 short sentences (max ~39 words / 200 characters);
- Start each bullet with a strong noun or action
- Focus on what matters to defenders and security practitioners
- No emojis, no hashtags, no marketing language
- Include the link to the original article at the next line following each bullet
- Insert line breaks between each bullet point and link pair
- Do not use "facilitate"

News items:
{news_block}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"AI summarization failed: {e}")
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