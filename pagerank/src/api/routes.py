# src/api/routes.py
from fastapi import APIRouter, HTTPException, Query
from urllib.parse import unquote, quote
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from src.graph_loader import load_graph
from src.services.pagerank_service import compute
from src.cache import save, get

logger = logging.getLogger(__name__)
router = APIRouter()

class UrlList(BaseModel):
    urls: List[str]

@router.post("/compute")
def compute_all():
    """
    Lance le calcul PageRank sur le graphe courant, stocke les scores en cache Redis
    et renvoie des infos de diagnostic.
    """
    graph = load_graph()
    node_count = len({*graph.keys(), *(v for dests in graph.values() for v in dests)})
    edge_count = sum(len(v) for v in graph.values())

    if edge_count == 0:
        return {"status": "ok", "node_count": node_count, "edge_count": edge_count, "count": 0}

    scores = compute(graph)
    save(scores)
    return {"status": "ok", "node_count": node_count, "edge_count": edge_count, "count": len(scores)}

def _get_score_with_fallback(key: str) -> Optional[float]:
    """
    Récupère score en essayant d'abord la clé 'key' (décodée),
    puis la version encodée si la première n'existe pas.
    """
    # try decoded key first
    score = get(key)
    if score is not None:
        return score
    # try encoded key fallback (some clients might have stored encoded keys)
    encoded = quote(key, safe='')
    return get(encoded)

@router.get("/{url}")
def read_score(url: str):
    """
    Path-based : /pagerank/http%3A%2F%2Fa.com  (note: path segments with slashes may be problematic)
    """
    decoded = unquote(url)
    score = _get_score_with_fallback(decoded)
    if score is None:
        raise HTTPException(status_code=404, detail=f"Aucun score pour {decoded}")
    return {"url": decoded, "score": score}

@router.get("/")
def read_score_q(url: str = Query(..., description="URL complète (ex: http://a.com)")):
    """
    Query-based : /pagerank/?url=http://a.com
    Décodage et fallback gérés.
    """
    decoded = unquote(url)
    score = _get_score_with_fallback(decoded)
    if score is None:
        raise HTTPException(status_code=404, detail=f"Aucun score pour {decoded}")
    return {"url": decoded, "score": score}

@router.get("/raw/{url:path}")
def read_score_raw(url: str):
    """
    Raw path capture (capture aussi les slashes) : /pagerank/raw/http://a.com
    Utile si tu veux éviter les soucis d'encoding / redirect.
    """
    decoded = unquote(url)
    score = _get_score_with_fallback(decoded)
    if score is None:
        raise HTTPException(status_code=404, detail=f"Aucun score pour {decoded}")
    return {"url": decoded, "score": score}

@router.post("/batch")
def read_batch(request: UrlList) -> Dict[str, Optional[float]]:
    """
    Batch : renvoie { requested_url: score_or_null }
    Les URLs peuvent être encodées ou non.
    """
    out: Dict[str, Optional[float]] = {}
    for u in request.urls:
        key = unquote(u)
        out[u] = _get_score_with_fallback(key)
    return out
