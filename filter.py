from typing import List, Dict, Iterable, Optional
import sys, json
import re

CYBER_KEYWORDS = [
    "malware", "ransomware", "phishing", "vulnerability", "exploit",
    "breach", "botnet", "zero-day", "zero day",
    "security", "hacking", "trojan", "worm", "spyware",
    "backdoor", "rootkit", "credential", "leak", "data leak", "data breach",
    "incident", "incident response", "threat", "attack", "virus", "cybersecurity",
    "cyber", "threat actor", "data extortion", "prompt injection", "adversarial AI", 
    "llm security", "zero trust", "post-quantum", "api security", "supply chain attack",
    "privilege escalation", "remote code execution", "sql injection", "malicious", "payload",
    "command and control", "lateral movement", "persistence", "cloud security",
    "remote code execution", "malicious link"
]

DEFAULT_FIELDS = ("title", "summary")

SHORT_WORDS = ["apt", "cve", "ddos", "edr", "rce", "iot", "xss", "c2", "dos"]
SHORT_PAT = re.compile(r"\b(" + "|".join(map(re.escape, SHORT_WORDS)) + r")\b", re.IGNORECASE)
def filter_items(items: Iterable[Dict]) -> List[Dict]:
    filtered = []

    for item in items:
        parts = []
        for f in DEFAULT_FIELDS:
            v = item.get(f)
            if v:
                parts.append(str(v))

        if not parts:
            continue

        text_raw = " ".join(parts)
        text = text_raw.casefold()

        # High-signal whole-word matches
        if SHORT_PAT.search(text_raw):
            filtered.append(item)
            continue

        # General keyword matching
        if any(k in text for k in CYBER_KEYWORDS):
            filtered.append(item)

    return filtered

