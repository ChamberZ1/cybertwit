import json
from pathlib import Path
from typing import Set, Iterable

STATE_PATH = Path("state/posted_links.json")

def load_posted_links() -> Set[str]:
    if not STATE_PATH.exists():
        return set()
    try:
        return set(json.loads(STATE_PATH.read_text(encoding="utf-8")))
    except Exception:
        return set()

def save_posted_links(links: Iterable[str]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = STATE_PATH.with_suffix(".tmp")
    tmp_path.write_text(
        json.dumps(sorted(set(links)), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    tmp_path.replace(STATE_PATH)
