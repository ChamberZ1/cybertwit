import sys
import json
from typing import List, Dict

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
            lines.append(f"• {title} ({source})")
        else:
            lines.append(f"• {title}")
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