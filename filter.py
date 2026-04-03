import json
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, List

DEFAULT_KEYWORDS = [
    "artificial intelligence",
    "ai security",
    "llm security",
    "model theft",
    "model poisoning",
    "data poisoning",
    "prompt injection",
    "adversarial ai",
    "ai alignment",
    "ai jailbreak",
    "training data leak",
    "model inversion",
    "inference attack",
    "large language model",
    "large language models",
    "openai",
    "gemini",
    "gpt-4",
    "claude",
    "anthropic",
    "cloud security",
    "cloud breach",
    "cloud misconfiguration",
    "api security",
    "api abuse",
    "exposed api",
    "iam misconfiguration",
    "privilege escalation",
    "identity compromise",
    "service account abuse",
    "container escape",
    "kubernetes attack",
    "supply chain attack",
    "azure",
    "critical infrastructure",
    "power grid",
    "electric grid",
    "energy sector",
    "scada",
    "ics security",
    "operational technology",
    "ot security",
    "industrial control system",
    "grid disruption",
    "substation",
    "utility provider",
    "drone security",
    "uav",
    "unmanned aerial vehicle",
    "autonomous system",
    "robotics security",
    "robot takeover",
    "navigation spoofing",
    "gps spoofing",
    "command hijacking",
    "remote control abuse",
    "firmware tampering",
    "drone",
    "drones",
    "robot",
    "robots",
    "robotics",
]

DEFAULT_SHORT_WORDS = ["ai", "llm", "rf", "uav", "aws"]
DEFAULT_FIELDS = ["title", "summary"]
FILTERS_PATH = Path("filters.json")


def load_filter_config() -> Dict[str, List[str]]:
    defaults = {
        "fields": DEFAULT_FIELDS,
        "keywords": DEFAULT_KEYWORDS,
        "short_words": DEFAULT_SHORT_WORDS,
    }

    if not FILTERS_PATH.exists():
        return defaults

    try:
        data = json.loads(FILTERS_PATH.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError("filters.json must contain a JSON object.")

        fields = data.get("fields", DEFAULT_FIELDS)
        keywords = data.get("keywords", DEFAULT_KEYWORDS)
        short_words = data.get("short_words", DEFAULT_SHORT_WORDS)

        if not isinstance(fields, list) or not all(isinstance(item, str) and item.strip() for item in fields):
            raise ValueError("filters.json field 'fields' must be a list of non-empty strings.")
        if not isinstance(keywords, list) or not all(isinstance(item, str) and item.strip() for item in keywords):
            raise ValueError("filters.json field 'keywords' must be a list of non-empty strings.")
        if not isinstance(short_words, list) or not all(isinstance(item, str) and item.strip() for item in short_words):
            raise ValueError("filters.json field 'short_words' must be a list of non-empty strings.")

        return {
            "fields": [item.strip() for item in fields],
            "keywords": [item.strip().casefold() for item in keywords],
            "short_words": [item.strip() for item in short_words],
        }
    except Exception as e:
        logging.warning(f"Failed to load filters.json ({e}), using defaults.")
        return defaults


def build_short_word_pattern(short_words: List[str]) -> re.Pattern[str] | None:
    if not short_words:
        return None

    return re.compile(
        r"\b(" + "|".join(map(re.escape, short_words)) + r")\b",
        re.IGNORECASE,
    )


def filter_items(items: Iterable[Dict]) -> List[Dict]:
    config = load_filter_config()
    fields = config["fields"]
    keywords = config["keywords"]
    short_pattern = build_short_word_pattern(config["short_words"])
    filtered = []

    for item in items:
        parts = []
        for field in fields:
            value = item.get(field)
            if value:
                parts.append(str(value))

        if not parts:
            continue

        text_raw = " ".join(parts)
        text = text_raw.casefold()

        if short_pattern and short_pattern.search(text_raw):
            filtered.append(item)
            continue

        if any(keyword in text for keyword in keywords):
            filtered.append(item)

    return filtered
