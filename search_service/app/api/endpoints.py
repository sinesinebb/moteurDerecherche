from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging
from elasticsearch import AsyncElasticsearch
from app.database.elasticsearch import get_elasticsearch_client

logger = logging.getLogger(__name__)

# Si vous avez un router dédié, sinon ajoutez directement dans main.py
router = APIRouter()

@app.get("/autocomplete")
async def autocomplete(
    q: str = Query(..., min_length=1, max_length=50, description="Terme de recherche pour l'autocomplétion"),
    size: int = Query(5, ge=1, le=20, description="Nombre de suggestions à retourner")
):
    """Suggestion automatique améliorée basée sur les titres et contenu existants"""
    try:
        if not es.indices.exists(index="tech_docs"):
            return {
                "query": q, 
                "suggestions": generate_fallback_suggestions(q, size),
                "count": size,
                "fallback": True
            }
        
        # REQUÊTE AMÉLIORÉE : Recherche plus intelligente
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match_phrase_prefix": {
                                "metadata.title": {
                                    "query": q,
                                    "slop": 5,
                                    "boost": 3.0
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": {
                                "text": {
                                    "query": q,
                                    "slop": 10,
                                    "boost": 1.0
                                }
                            }
                        },
                        {
                            "wildcard": {
                                "metadata.title": {
                                    "value": f"*{q}*",
                                    "boost": 2.0
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "size": min(size * 3, 50),  # Plus de résultats pour diversifier
            "_source": ["metadata.title", "text"],
            "highlight": {
                "fields": {
                    "metadata.title": {
                        "fragment_size": 50,
                        "number_of_fragments": 1
                    },
                    "text": {
                        "fragment_size": 100,
                        "number_of_fragments": 1
                    }
                }
            },
            "sort": ["_score"]
        }
        
        logger.info(f"🔍 Autocomplete pour: '{q}'")
        response = es.search(index="tech_docs", body=search_body)
        
        suggestions = set()
        
        # 1. Extraire les titres pertinents
        for hit in response['hits']['hits']:
            source = hit['_source']
            title = source.get('metadata', {}).get('title', '').strip()
            
            if title and len(title) > len(q) + 2:
                # Vérifier que le titre contient la requête
                if q.lower() in title.lower():
                    suggestions.add(title)
            
            # 2. Extraire des extraits pertinents du texte
            text_content = source.get('text', '')
            if text_content and len(suggestions) < size * 2:
                # Chercher des phrases contenant la requête
                text_suggestions = extract_text_suggestions(text_content, q, max_suggestions=2)
                suggestions.update(text_suggestions)
            
            # Limiter le nombre de suggestions par document
            if len(suggestions) >= size * 2:
                break
        
        # 3. Si pas assez de suggestions, générer des variations intelligentes
        if len(suggestions) < 3:
            variations = generate_smart_variations(q, size - len(suggestions))
            suggestions.update(variations)
        
        # Trier par pertinence (longueur et présence au début)
        final_suggestions = sorted(
            list(suggestions),
            key=lambda x: (
                -len(x),  # Préférer les suggestions plus longues
                0 if x.lower().startswith(q.lower()) else 1,  # Préférer celles qui commencent par la requête
                x.lower().index(q.lower()) if q.lower() in x.lower() else 999  # Position de la requête
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
        # Fallback robuste
        fallback_suggestions = generate_fallback_suggestions(q, size)
        return {
            "query": q,
            "suggestions": fallback_suggestions,
            "count": len(fallback_suggestions),
            "fallback": True,
            "error": str(e)
        }

def extract_text_suggestions(text: str, query: str, max_suggestions: int = 2) -> list:
    """Extrait des suggestions pertinentes du texte"""
    suggestions = set()
    query_lower = query.lower()
    text_lower = text.lower()
    
    # Trouver toutes les occurrences de la requête
    start_pos = 0
    occurrences = []
    
    while True:
        pos = text_lower.find(query_lower, start_pos)
        if pos == -1:
            break
        occurrences.append(pos)
        start_pos = pos + 1
    
    # Extraire des extraits autour de chaque occurrence
    for pos in occurrences[:max_suggestions * 2]:  # Limiter le traitement
        # Prendre 5-8 mots autour de l'occurrence
        words = text.split()
        
        # Trouver l'index du mot contenant la requête
        current_pos = 0
        word_index = -1
        for i, word in enumerate(words):
            if current_pos <= pos < current_pos + len(word):
                word_index = i
                break
            current_pos += len(word) + 1
        
        if word_index != -1:
            # Extraire une phrase de 5-8 mots
            start = max(0, word_index - 3)
            end = min(len(words), word_index + 5)
            phrase = ' '.join(words[start:end])
            
            # Nettoyer et valider la phrase
            phrase = phrase.strip()
            if len(phrase) > len(query) + 10 and len(phrase) < 150:
                suggestions.add(phrase + "...")
    
    return list(suggestions)[:max_suggestions]

def generate_smart_variations(query: str, count: int) -> list:
    """Génère des variations intelligentes basées sur le domaine informatique"""
    variations = []
    query_lower = query.lower()
    
    # Patterns généraux pour l'informatique
    general_patterns = [
        f"{query} programmation",
        f"{query} tutoriel",
        f"{query} documentation",
        f"{query} développement",
        f"{query} cours",
        f"{query} guide",
        f"{query} installation",
        f"{query} configuration",
        f"apprendre {query}",
        f"comment utiliser {query}",
        f"{query} examples",
        f"{query} code source",
        f"{query} erreurs courantes",
        f"{query} meilleures pratiques"
    ]
    
    # Patterns spécifiques par technologie
    tech_specific = {
        "python": [
            "python django", "python flask", "python pandas", "python numpy",
            "python machine learning", "python web scraping", "python automation"
        ],
        "java": [
            "java spring", "java hibernate", "java maven", "java spring boot",
            "java microservices", "java jvm", "java performance"
        ],
        "javascript": [
            "javascript react", "javascript node", "javascript vue", "javascript angular",
            "javascript typescript", "javascript frontend", "javascript backend"
        ],
        "docker": [
            "docker compose", "docker kubernetes", "docker swarm", "docker containers",
            "docker images", "docker networking", "docker volumes"
        ],
        "react": [
            "react hooks", "react components", "react state", "react props",
            "react native", "react router", "react context"
        ],
        "vue": [
            "vue 3", "vue composition api", "vue router", "vuex",
            "vue components", "vue directives", "vue lifecycle"
        ],
        "mysql": [
            "mysql database", "mysql queries", "mysql performance", "mysql indexes",
            "mysql replication", "mysql backup", "mysql optimization"
        ],
        "git": [
            "git commands", "git branches", "git merge", "git rebase",
            "git workflow", "git hooks", "git submodules"
        ]
    }
    
    # Ajouter des variations spécifiques si la technologie est reconnue
    for tech, specific_variations in tech_specific.items():
        if tech in query_lower:
            variations.extend(specific_variations)
    
    variations.extend(general_patterns)
    
    # Dédupliquer et limiter
    unique_variations = []
    for variation in variations:
        if variation not in unique_variations and len(unique_variations) < count:
            unique_variations.append(variation)
    
    return unique_variations

def generate_fallback_suggestions(query: str, count: int) -> list:
    """Génère des suggestions de fallback robustes"""
    fallback = [
        f"{query} programmation",
        f"{query} tutoriel", 
        f"{query} documentation",
        f"apprendre {query}",
        f"{query} développement",
        f"{query} cours",
        f"{query} guide",
        f"{query} informatique"
    ]
    return fallback[:count]