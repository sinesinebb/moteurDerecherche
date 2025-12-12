# src/processors/nlp_processor.py
"""
NLP utilities used by the indexing pipeline.

Design goals:
- pas de dépendances lourdes obligatoires (fonctionne "out of the box")
- si des dépendances (langdetect, spacy, sentence-transformers) sont présentes, elles sont utilisées
- fonctions déterministes utiles pour tests / POC

Fonctions exposées:
- normalize_text(text) -> str
- tokenize(text) -> list[str]
- extract_text_from_raw_response(item) -> str
- embedding_from_text(text, dims=128) -> list[float]  (deterministic fallback using SHA256)
"""

from __future__ import annotations
import re
import hashlib
import time
from typing import List, Mapping, Any, Optional

# Optional dependencies
try:
    from langdetect import detect as _lang_detect  # type: ignore
except Exception:
    _lang_detect = None  # type: ignore

# If you have a real model installed (e.g. sentence-transformers),
# you can plug it in by calling set_text_embedding_model(...)
_embedding_model = None


def set_text_embedding_model(model_callable):
    """
    Permet d'injecter un callable model_callable(text: str) -> list[float]
    Exemple: model_callable = lambda s: model.encode(s).tolist()
    """
    global _embedding_model
    _embedding_model = model_callable


_whitespace_re = re.compile(r"\s+")


def normalize_text(text: Optional[str]) -> str:
    """Lowercase + collapse whitespace + strip. Returns empty string if None."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    # optional: keep case for code detection? For now lowercase.
    text = text.lower()
    text = _whitespace_re.sub(" ", text)
    return text


_token_re = re.compile(r"\b[\w']+\b", flags=re.UNICODE)


def tokenize(text: Optional[str]) -> List[str]:
    """Very small tokenizer splitting on words. Returns empty list if no text."""
    t = normalize_text(text)
    if not t:
        return []
    return _token_re.findall(t)


def detect_language(text: str) -> str:
    """Try to detect language, fallback to 'und'."""
    if not text:
        return "und"
    if _lang_detect:
        try:
            return _lang_detect(text)
        except Exception:
            return "und"
    return "und"


def extract_text_from_raw_response(item: Mapping[str, Any]) -> str:
    """
    Given a RawResponseItem-like mapping (crawler output),
    returns a concatenated textual field used for indexing.
    Expected keys: body, title, description, keywords_found (list)
    """
    pieces = []
    if not item:
        return ""
    # prefer provided explicit fields
    for k in ("title", "description"):
        v = item.get(k) if isinstance(item, dict) else None
        if v:
            pieces.append(str(v))
    # body may be large HTML or already cleaned text
    body = item.get("body") or item.get("text") or ""
    if body:
        pieces.append(str(body))
    # keywords_found could be an iterable
    kf = item.get("keywords_found") or item.get("keywords") or []
    if isinstance(kf, (list, tuple)):
        pieces.append(" ".join(map(str, kf)))
    return "\n\n".join([p for p in pieces if p])


def _sha256_to_floats(text: str, dims: int) -> List[float]:
    """
    Deterministic pseudo-embedding using SHA256. Splits digest bytes into dims buckets.
    Values normalized to [-1, 1].
    Good for testing and for deterministic behavior when no real model is installed.
    """
    if dims <= 0:
        return []
    # base bytes from text + timestamp-insensitive
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # expand digest deterministically if dims > len(h)
    out = []
    # take repeated hashing rounds to get enough bytes
    rounds = (dims * 4 + len(h) - 1) // len(h)
    data = h
    for i in range(1, rounds):
        data += hashlib.sha256(h + i.to_bytes(2, "big")).digest()
    # convert to floats
    for i in range(dims):
        # take 4 bytes per float
        start = (i * 4) % len(data)
        chunk = data[start:start + 4]
        if len(chunk) < 4:
            chunk = chunk.ljust(4, b"\0")
        val = int.from_bytes(chunk, "big", signed=False)
        # normalize 0..2**32-1 -> -1..1
        f = (val / 0xFFFFFFFF) * 2.0 - 1.0
        out.append(f)
    return out


def embedding_from_text(text: str, dims: int = 128) -> List[float]:
    """
    Return an embedding for `text`.
    - If an embedding model has been set with set_text_embedding_model(), it will be used.
    - Otherwise falls back to a deterministic SHA256-based vector of length `dims`.
    """
    if _embedding_model is not None:
        try:
            vec = _embedding_model(text)
            # coerce to list[float] and/or truncate/pad
            vec = list(vec)
            if dims and len(vec) != dims:
                # try to adapt: truncate or pad with zeros
                if len(vec) > dims:
                    return vec[:dims]
                else:
                    return vec + [0.0] * (dims - len(vec))
            return vec
        except Exception:
            # fall back to deterministic
            pass
    return _sha256_to_floats(text or "", dims)
