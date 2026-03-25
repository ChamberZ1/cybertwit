from typing import List, Dict, Iterable
import re

CYBER_KEYWORDS = [
    # --- Artificial Intelligence / LLM Security ---
    "artificial intelligence", "ai security", "llm security", "model theft",
    "model poisoning", "data poisoning", "prompt injection",
    "adversarial ai", "ai alignment", "ai jailbreak",
    "training data leak", "model inversion", "inference attack", "large language model", "large language models",
    "openai", "gemini", "gpt-4", "claude", "anthropic",


    # --- Cloud & API Security ---
    "cloud security", "cloud breach", "cloud misconfiguration",
    "api security", "api abuse", "exposed api",
    "iam misconfiguration", "privilege escalation",
    "identity compromise", "service account abuse",
    "container escape", "kubernetes attack", "supply chain attack", "azure",

    # --- Critical Infrastructure / Power Grid / OT ---
    "critical infrastructure", "power grid", "electric grid",
    "energy sector", "scada", "ics security",
    "operational technology", "ot security",
    "industrial control system", "grid disruption",
    "substation", "utility provider",

    # --- Drones / Robotics / Autonomous Systems ---
    "drone security", "uav", "unmanned aerial vehicle",
    "autonomous system", "robotics security",
    "robot takeover", "navigation spoofing",
    "gps spoofing", "command hijacking",
    "remote control abuse", "firmware tampering", "drone", "drones",
    "robot", "robots", "robotics", 

]


DEFAULT_FIELDS = ("title", "summary")

SHORT_WORDS = ["ai", "llm", "rf", "uav", "aws"]
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

