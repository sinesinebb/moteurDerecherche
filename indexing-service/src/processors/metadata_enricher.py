# src/processors/metadata_enricher.py
"""
Enrichit les métadonnées d'un document avant indexation.

Fonctions exposées:
- enrich_metadata(doc) -> dict
  doc peut être un dict ou un objet avec attributs .url, .metadata, .title, ...
  La fonction renvoie une nouvelle dict (copie légère) enrichie.
"""

from __future__ import annotations
from typing import Any, Mapping, MutableMapping, Dict
from datetime import datetime
from urllib.parse import urlparse
import hashlib

# optional language detection (reused from nlp_processor if available)
try:
    from src.processors.nlp_processor import detect_language, tokenize  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    def detect_language(text: str) -> str:  # type: ignore
        return "und"
    def tokenize(text: str):
        return []

def _safe_get_text(doc: Any) -> str:
    if not doc:
        return ""
    if isinstance(doc, dict):
        # prefer fields commonly present
        for key in ("text", "body", "title", "description"):
            if key in doc and doc[key]:
                return str(doc[key])
        return ""
    # object: try attributes
    for attr in ("text", "body", "title", "description"):
        if hasattr(doc, attr):
            val = getattr(doc, attr)
            if val:
                return str(val)
    return ""


def _extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        return host.lower()
    except Exception:
        return ""


def enrich_metadata(doc: Any) -> Dict[str, Any]:
    """
    Return a dict with at least:
    - id: existing id or computed hash
    - source_domain: parsed from url if any
    - language: detected if possible
    - tokens_count, tokens (short list)
    - extracted_at: ISO timestamp
    - metadata: copy of original metadata (if present)
    """
    result: Dict[str, Any] = {}

    # read baseline fields
    if isinstance(doc, dict):
        src = dict(doc)  # shallow copy
        metadata = dict(doc.get("metadata") or {})
        url = doc.get("url") or doc.get("response_url") or ""
        _id = doc.get("id") or doc.get("doc_id") or None
    else:
        # object
        src = {}
        metadata = dict(getattr(doc, "metadata", {}) or {})
        url = getattr(doc, "url", "") or getattr(doc, "response_url", "")
        _id = getattr(doc, "id", None) or getattr(doc, "doc_id", None)

    # id: generate if absent
    if not _id:
        # deterministic id from url or text
        base = url or _safe_get_text(doc) or str(time.time())
        _id = hashlib.sha1(base.encode("utf-8")).hexdigest()

    result["id"] = _id
    result["url"] = url
    result["source_domain"] = _extract_domain(url) if url else ""
    text = _safe_get_text(doc)
    result["text_sample"] = (text[:200] + "...") if len(text) > 200 else text
    # language detection best-effort
    result["language"] = detect_language(text) if text else "und"
    # tokens (first 40 tokens)
    toks = tokenize(text) if text else []
    result["tokens_count"] = len(toks)
    result["tokens"] = toks[:40]
    result["extracted_at"] = datetime.utcnow().isoformat() + "Z"
    # preserve or attach metadata dict
    result["metadata"] = metadata
    # keep original fields that might be used downstream
    if isinstance(doc, dict):
        for k in ("title", "description", "status_code", "keywords_found"):
            if k in doc:
                result[k] = doc[k]
    else:
        # try attributes
        for k in ("title", "description", "status_code", "keywords_found"):
            if hasattr(doc, k):
                result[k] = getattr(doc, k)

    return result
