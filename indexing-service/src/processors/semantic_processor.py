# src/processors/semantic_processor.py
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.processors.nlp_processor import embedding_from_text, set_text_embedding_model, extract_text_from_raw_response, normalize_text
from elasticsearch import Elasticsearch
import numpy as np

logger = logging.getLogger("indexing-service.semantic_processor")

# Optional: try to load sentence-transformers if available
_EMBED_DIMS_OVERRIDE = int(os.getenv("EMBEDDING_DIMS", "384"))  # default small
_embedding_source = os.getenv("EMBEDDING_BACKEND", "local").lower()

# If using sentence-transformers locally, you can inject model callable via set_text_embedding_model
# Example in main: from sentence_transformers import SentenceTransformer; set_text_embedding_model(lambda s: model.encode(s).tolist())

def compute_embedding(text: str, dims: Optional[int] = None) -> List[float]:
    """Compute embedding using nlp_processor fallback."""
    dims = dims or _EMBED_DIMS_OVERRIDE
    emb = embedding_from_text(text or "", dims=dims)
    return emb

def classify_category_by_keywords(text: str, keywords_map: Dict[str, List[str]]) -> str:
    """Quick heuristic classifier based on keyword lists."""
    tl = normalize_text(text)
    scores = {}
    for cat, kws in keywords_map.items():
        count = sum(1 for kw in kws if kw in tl)
        scores[cat] = count
    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "general"

def compute_quality_score(doc: Dict[str, Any]) -> float:
    """Multi-factor quality score in [0,1]."""
    content = doc.get("extracted_content") or doc.get("content") or ""
    length_score = min(1.0, len(content) / 2000)  # longer better up to 2000 chars
    images = len(doc.get("image_urls", []))
    videos = len(doc.get("video_urls", []))
    media_score = min(1.0, (images + videos) / 5)
    code_bonus = 1.0 if ("def " in content or "class " in content or "function " in content) else 0.0
    domain_auth = float(doc.get("domain_authority", 50)) / 100.0
    score = 0.5*length_score + 0.2*media_score + 0.1*code_bonus + 0.2*domain_auth
    return max(0.0, min(1.0, score))

def is_duplicate(es: Elasticsearch, index: str, embedding: List[float], threshold: float = 0.87, size: int = 5, vector_field: str = "embedding") -> Optional[Dict]:
    """
    Query ES for nearest neighbors using KNN/search_by_vector (works on ES 8+ or with appropriate plugin).
    Returns nearest hit if similarity >= threshold (cosine).
    """
    if es is None or embedding is None:
        return None
    # Use script_score cosine fallback if dense_vector cannot be used for kNN in your ES version:
    try:
        # prefer kNN search (more efficient) if available:
        body = {
            "knn": {
                vector_field: {
                    "vector": embedding,
                    "k": size
                }
            },
            "_source": {"includes": ["url", "metadata", "timestamp", "title"]}
        }
        res = es.search(index=index, body=body)
        hits = res.get("hits", {}).get("hits", [])
        if hits:
            top = hits[0]
            # Score from kNN is similarity measure on some ES versions; otherwise compute cosine manually if we have embedding stored.
            score = top.get("_score", None)
            # If score is None or not cosine, compute approximate via script? Fallback: accept first if score is high enough
            if score is not None and score >= threshold:
                return top
            # else fallback: compute cosine with stored embedding if stored in _source
            src_emb = top.get("_source", {}).get(vector_field)
            if src_emb:
                v1 = np.array(embedding, dtype=float)
                v2 = np.array(src_emb, dtype=float)
                cos = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9))
                if cos >= threshold:
                    return top
    except Exception as exc:
        logger.debug("kNN search failed (try script_score): %s", exc)

    # fallback script_score search (cosine)
    try:
        script_query = {
            "size": 1,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, doc['{}']) + 1.0".format(vector_field),
                        "params": {"query_vector": embedding}
                    }
                }
            },
            "_source": {"includes": ["url","metadata","timestamp","title","embedding"]}
        }
        res = es.search(index=index, body=script_query)
        hits = res.get("hits", {}).get("hits", [])
        if hits:
            top = hits[0]
            score = top.get("_score", 0.0)
            # script_score is cosine+1.0, so normalize
            cos = score - 1.0
            if cos >= threshold:
                return top
    except Exception as exc:
        logger.debug("script_score search failed: %s", exc)

    return None

# petit aide pour un build sémantic correcte lors que le document est prets pour ES 
def build_semantic_doc(raw_doc: Dict[str,Any], embedding_dims:int=384, keywords_map:Optional[Dict[str,List[str]]]=None) -> Dict[str,Any]:
    """
    - compute embedding from extracted text
    - classify basic category by keywords
    - compute quality_score
    - attach timestamp
    """
    content = raw_doc.get("extracted_content") or raw_doc.get("body") or raw_doc.get("content") or ""
    text_for_embed = content if len(content.strip())>20 else (raw_doc.get("title","") + " " + raw_doc.get("description",""))
    emb = compute_embedding(text_for_embed, dims=embedding_dims)
    raw_doc["embedding"] = emb
    raw_doc["embedding_dims"] = len(emb)
    # catégories
    if keywords_map:
        raw_doc["category"] = classify_category_by_keywords(text_for_embed, keywords_map)
    else:
        raw_doc["category"] = raw_doc.get("content_type","general")
    raw_doc["quality_score"] = compute_quality_score(raw_doc)
    raw_doc["semantic_indexed_at"] = datetime.utcnow().isoformat()
    return raw_doc
