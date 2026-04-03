import feedparser
import logging
import requests
from typing import List, Dict, Tuple
from dateutil import parser as date_parser
from datetime import datetime, timedelta, timezone
import html
from bs4 import BeautifulSoup
from feeds import load_feeds

HEADERS = {
    "User-Agent": "cybertwit-bot/6.9"
}

def clean_html(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def fetch_rss_feeds(feeds: List[Tuple[str, str]]) -> List[Dict]:
    articles = []
    seen_links = set()
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)

    for source_name, url in feeds:
        try:
            resp = requests.get(url, timeout=20, headers=HEADERS)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)

            for entry in feed.entries:
                link = entry.get("link", "").strip()
                if not link or link in seen_links:
                    continue

                published = None 
                if "published" in entry:
                    try:
                        published = date_parser.parse(entry.published)  # parse the date string from the feed (e.g. "Thu, 01 Apr 2026 14:00:00 GMT")

                        # normalize to UTC for consistent comparison.
                        if published.tzinfo is None:
                            published = published.replace(tzinfo=timezone.utc)  # if no timezone info, assume UTC
                        else:
                            published = published.astimezone(timezone.utc)  # otherwise convert to UTC
                    except Exception as e:
                        logging.warning(f"Could not normalize datetime for entry '{entry.get('title', 'unknown')}': {e}")  # log errors

                if published and published < time_threshold:
                    continue

                seen_links.add(link)

                articles.append({
                    "title": clean_html(entry.get("title", "").strip()),
                    "link": link,
                    "summary": clean_html(entry.get("summary", "").strip()),
                    "published": published,
                    "source": source_name,
                })

        except Exception as e:
            logging.error(f"Error fetching {source_name}: {e}")

    return articles


if __name__ == "__main__":
    feeds = load_feeds()
    items = fetch_rss_feeds(feeds)
    for item in items:
        print(f"- [{item['source']}] {item['title']}\n  \nSummary: {item['summary']} \n\nFull article: {item['link']}\n")
