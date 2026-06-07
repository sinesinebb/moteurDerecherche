# app/api/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging
from elasticsearch import AsyncElasticsearch
from app.database.elasticsearch import get_elasticsearch_client
from app.services.search_engine import AdvancedSearchEngine
from app.models.schemas import SearchRequest, SearchResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# ----------------------------------------------------------------------
# Helpers d'autocomplétion (inchangés)
# ----------------------------------------------------------------------
def extract_text_suggestions(text: str, query: str, max_suggestions: int = 2) -> list:
    """Extrait des suggestions pertinentes du texte"""
    suggestions = set()
    query_lower = query.lower()
    text_lower = text.lower()
    
    start_pos = 0
    occurrences = []
    while True:
        pos = text_lower.find(query_lower, start_pos)
        if pos == -1:
            break
        occurrences.append(pos)
        start_pos = pos + 1
    
    for pos in occurrences[:max_suggestions * 2]:
        words = text.split()
        current_pos = 0
        word_index = -1
        for i, word in enumerate(words):
            if current_pos <= pos < current_pos + len(word):
                word_index = i
                break
            current_pos += len(word) + 1
        
        if word_index != -1:
            start = max(0, word_index - 3)
            end = min(len(words), word_index + 5)
            phrase = ' '.join(words[start:end])
            phrase = phrase.strip()
            if len(phrase) > len(query) + 10 and len(phrase) < 150:
                suggestions.add(phrase + "...")
    
    return list(suggestions)[:max_suggestions]


def generate_smart_variations(query: str, count: int) -> list:
    """Génère des variations intelligentes basées sur le domaine informatique"""
    variations = []
    query_lower = query.lower()
    
    general_patterns = [
        f"{query} programmation", f"{query} tutoriel", f"{query} documentation",
        f"{query} développement", f"{query} cours", f"{query} guide",
        f"{query} installation", f"{query} configuration",
        f"apprendre {query}", f"comment utiliser {query}",
        f"{query} examples", f"{query} code source",
        f"{query} erreurs courantes", f"{query} meilleures pratiques"
    ]
    
    tech_specific = {
        "python": ["python django", "python flask", "python pandas", "python numpy"],
        "java": ["java spring", "java hibernate", "java maven"],
        "javascript": ["javascript react", "javascript node", "javascript vue"],
        "docker": ["docker compose", "docker kubernetes", "docker swarm"],
        "react": ["react hooks", "react components", "react state"],
        "vue": ["vue 3", "vue composition api", "vue router"],
        "mysql": ["mysql database", "mysql queries", "mysql performance"],
        "git": ["git commands", "git branches", "git merge"]
    }
    
    for tech, specific_variations in tech_specific.items():
        if tech in query_lower:
            variations.extend(specific_variations)
    
    variations.extend(general_patterns)
    unique_variations = []
    for variation in variations:
        if variation not in unique_variations and len(unique_variations) < count:
            unique_variations.append(variation)
    return unique_variations


def generate_fallback_suggestions(query: str, count: int) -> list:
    """Génère des suggestions de fallback robustes"""
    fallback = [
        f"{query} programmation", f"{query} tutoriel", f"{query} documentation",
        f"apprendre {query}", f"{query} développement", f"{query} cours",
        f"{query} guide", f"{query} informatique"
    ]
    return fallback[:count]


# ----------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------

@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(..., min_length=1, max_length=50, description="Terme de recherche pour l'autocomplétion"),
    size: int = Query(5, ge=1, le=20, description="Nombre de suggestions à retourner"),
    es: AsyncElasticsearch = Depends(get_elasticsearch_client)
):
    """Suggestion automatique améliorée basée sur les titres et contenu existants"""
    try:
        # Vérification de l'existence de l'index
        if not await es.indices.exists(index="tech_docs"):
            return {
                "query": q,
                "suggestions": generate_fallback_suggestions(q, size),
                "count": size,
                "fallback": True
            }
        
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {"match_phrase_prefix": {"metadata.title": {"query": q, "slop": 5, "boost": 3.0}}},
                        {"match_phrase_prefix": {"text": {"query": q, "slop": 10, "boost": 1.0}}},
                        {"wildcard": {"metadata.title": {"value": f"*{q}*", "boost": 2.0}}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "size": min(size * 3, 50),
            "_source": ["metadata.title", "text"],
            "highlight": {
                "fields": {
                    "metadata.title": {"fragment_size": 50, "number_of_fragments": 1},
                    "text": {"fragment_size": 100, "number_of_fragments": 1}
                }
            },
            "sort": ["_score"]
        }
        
        logger.info(f"🔍 Autocomplete pour: '{q}'")
        response = await es.search(index="tech_docs", body=search_body)
        
        suggestions = set()
        for hit in response['hits']['hits']:
            source = hit['_source']
            title = source.get('metadata', {}).get('title', '').strip()
            if title and len(title) > len(q) + 2 and q.lower() in title.lower():
                suggestions.add(title)
            
            text_content = source.get('text', '')
            if text_content and len(suggestions) < size * 2:
                text_suggestions = extract_text_suggestions(text_content, q, max_suggestions=2)
                suggestions.update(text_suggestions)
            
            if len(suggestions) >= size * 2:
                break
        
        if len(suggestions) < 3:
            variations = generate_smart_variations(q, size - len(suggestions))
            suggestions.update(variations)
        
        final_suggestions = sorted(
            list(suggestions),
            key=lambda x: (
                -len(x),
                0 if x.lower().startswith(q.lower()) else 1,
                x.lower().index(q.lower()) if q.lower() in x.lower() else 999
            )
        )[:size]
        
        logger.info(f"✅ Autocomplete: {len(final_suggestions)} suggestions pour '{q}'")
        return {
            "query": q,
            "suggestions": final_suggestions,
            "count": len(final_suggestions),
            "total_hits": response['hits']['total']['value']
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur d'autocomplétion pour '{q}': {e}")
        fallback_suggestions = generate_fallback_suggestions(q, size)
        return {
            "query": q,
            "suggestions": fallback_suggestions,
            "count": len(fallback_suggestions),
            "fallback": True,
            "error": str(e)
        }


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Termes de recherche"),
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    sort_by: Optional[str] = None,
    content_type: Optional[str] = None,
    domains: Optional[List[str]] = Query(None),
    technical_level: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_score: Optional[float] = None,
    es: AsyncElasticsearch = Depends(get_elasticsearch_client)
):
    """
    Recherche avancée avec filtrage par type de contenu.
    content_type peut être 'videos', 'documentation', 'article', etc.
    """
    filters = {}
    
    if domains:
        filters['domains'] = domains
    if technical_level:
        filters['technical_level'] = [technical_level]
    if date_from or date_to:
        filters['date_range'] = {
            'start': date_from,
            'end': date_to
        }
    if min_score is not None:
        filters['min_page_rank'] = min_score
        
    # *** Filtrage vidéo ***
    if content_type == "videos":
        filters['content_types'] = ["youtube_video", "video"]
    elif content_type:
        filters['content_types'] = [content_type]
    
    search_request = SearchRequest(
        query=q,
        page=page,
        size=size,
        sort_by=sort_by,
        filters=filters
    )
    
    search_engine = AdvancedSearchEngine(es)
    response = await search_engine.search(search_request)
    return response