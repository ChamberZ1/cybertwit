import json
import logging
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse

DEFAULT_FEEDS = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("CISA", "https://www.cisa.gov/cybersecurity-advisories/all.xml"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml"),
    ("Google Security Blog", "https://security.googleblog.com/feeds/posts/default"),
    ("Schneier on Security", "https://www.schneier.com/feed/atom/"),
]

FEEDS_PATH = Path("feeds.json")


def load_feeds() -> List[Tuple[str, str]]:
    if not FEEDS_PATH.exists():
        return DEFAULT_FEEDS

    data = json.loads(FEEDS_PATH.read_text(encoding="utf-8"))
    feeds = []

    if not isinstance(data, list):
        raise ValueError("feeds.json must contain a JSON array.")

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each feed entry must be a JSON object.")

        name = str(item.get("name", "")).strip()
        url = str(item.get("url", "")).strip()

        if not name or not url:
            raise ValueError("Each feed entry must include non-empty 'name' and 'url' values.")

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            logging.warning(f"Skipping feed '{name}': invalid URL '{url}'")
            continue

        feeds.append((name, url))

    if not feeds:
        raise ValueError("feeds.json must contain at least one feed.")

    return feeds
