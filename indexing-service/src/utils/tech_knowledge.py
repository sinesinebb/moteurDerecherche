# src/utils/tech_knowledge.py
"""
Tiny helper to expose domain-specific knowledge (TechKG placeholder).
This is intentionally small: returns simple tag lookups from JSON files under /app/lib/TechKG if present.
"""
import os
import json
from typing import Dict, Any, Optional, List

_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "lib", "TechKG")
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib", "TechKG"))

def load_knowledge_file(name: str) -> Optional[Dict[str, Any]]:
    path = os.path.join(_BASE_DIR, name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf8") as fh:
            return json.load(fh)
    except Exception:
        return None

class TechKnowledge:
    def __init__(self):
        self._cache = {}

    def get_topic(self, topic_name: str) -> Optional[Dict[str, Any]]:
        if topic_name in self._cache:
            return self._cache[topic_name]
        # try file `topic_name.json`
        res = load_knowledge_file(f"{topic_name}.json")
        if res is not None:
            self._cache[topic_name] = res
        return res

    def list_available(self) -> List[str]:
        if not os.path.isdir(_BASE_DIR):
            return []
        return [f for f in os.listdir(_BASE_DIR) if f.endswith(".json")]
