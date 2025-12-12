# src/processors/document_cleaner.py
import re
from typing import Tuple

BOILERPLATE_PATTERNS = [
    r"^\s*cookie.*$",
    r"^\s*subscribe.*$",
    r"^.*all rights reserved.*$"
]

def remove_boilerplate(text: str) -> str:
    lines = text.splitlines()
    filtered = []
    for ln in lines:
        skip = False
        for pat in BOILERPLATE_PATTERNS:
            if re.search(pat, ln, flags=re.IGNORECASE):
                skip = True
                break
        if not skip:
            filtered.append(ln)
    cleaned = "\n".join(filtered)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def normalize_whitespace(text: str) -> str:
    return re.sub(r"[ \t]{2,}", " ", text).strip()
