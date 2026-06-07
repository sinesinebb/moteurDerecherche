# search_service/app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import time
import requests
import json
import os
import aiohttp
import asyncio
from collections import Counter
from sentence_transformers import CrossEncoder
import re
import redis.asyncio as redis
redis_client = None



# Initialiser le cross-encoder (si indisponible, désactiver)
try:
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cpu')
except Exception as e:
    logging.warning(f"CrossEncoder non disponible : {e}")
    cross_encoder = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Search Service API", description="Microservice de recherche spécialisé en informatique", version="4.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

ELASTICSEARCH_URL = "http://elasticsearch:9200"
INDEX_NAME = "tech_docs"
NLP_SERVICE_URL = os.getenv("NLP_SERVICE_URL", "http://nlp-service:8003")
PAGERANK_SERVICE_URL = os.getenv("PAGERANK_SERVICE_URL", "http://pagerank-service:8006")

http_session = None

class SearchRequest(BaseModel):
    query: str
    size: int = 10
    page: int = 1
    content_type: Optional[str] = "all"
    programming_language: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    has_code_examples: Optional[bool] = None
    sort_by: Optional[str] = "relevance"
    platforms: Optional[List[str]] = None
    file_type: Optional[str] = None

class TechnicalSearchRequest(SearchRequest):
    technical_concepts: Optional[List[str]] = None
    min_technical_score: Optional[float] = 0.3

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    query: str
    processing_time: float
    page: int
    total_pages: int
    content_type: str
    suggestions: Optional[List[str]] = None
    technical_facets: Optional[Dict[str, Any]] = None
    ranking_method: Optional[str] = "standard"
    is_informatics_domain: bool = True
    domain_message: Optional[str] = None

class TechnicalQueryAnalyzer:
    def __init__(self):
        # Synonymes techniques enrichis (abréviations, variantes)
        self.tech_synonyms = {
            "python": ["py", "python3", "programmation python"],
            "javascript": ["js", "ecmascript", "nodejs", "vanilla js"],
            "java": ["jdk", "jvm"],
            "docker": ["conteneur", "container", "dockerfile"],
            "api": ["interface", "rest", "graphql"],
            "base de données": ["database", "db", "sql", "nosql"],
            "machine learning": ["ml", "apprentissage automatique", "ia", "intelligence artificielle"],
            "deep learning": ["dl", "apprentissage profond", "réseaux de neurones"],
            "git": ["github", "gitlab", "versionning"],
            "linux": ["ubuntu", "debian", "centos", "bash"],
            "windows": ["win", "microsoft"],
            "macos": ["mac", "apple"],
            "c++": ["cpp"],
            "c#": ["csharp", "dotnet"],
            "go": ["golang"],
            "rust": ["rustlang"],
            "sql": ["mysql", "postgresql"],
            "cloud": ["aws", "azure", "gcp"],
            "devops": ["ci/cd", "kubernetes", "k8s"],
            "frontend": ["ui", "ux"],
            "backend": ["serveur", "api"],
            "typescript": ["ts"],
            "react": ["reactjs", "react.js"],
            "vue": ["vuejs", "vue.js"],
            "angular": ["angularjs", "angular.js"],
            "sécurité": ["cybersécurité", "cyber", "infosec"],
        }
        self.search_intents = {
            "tutorial": ["comment", "apprendre", "tutoriel", "guide"],
            "error": ["erreur", "bug", "problème", "solution"],
            "comparison": ["vs", "comparaison", "différence"],
            "documentation": ["doc", "référence", "manuel", "api"],
            "installation": ["installer", "setup", "configuration"],
            "optimization": ["performance", "optimiser"],
            "best_practices": ["bonnes pratiques", "pattern"],
        }

        # ----------------------------------------------------------------
        # Liste de mots clairement hors informatique (français + anglais)
        # ----------------------------------------------------------------
        self.NON_INFORMATICS_KEYWORDS = {
            # Cuisine / alimentation
            "recette", "cuisine", "gâteau", "pâtisserie", "pain", "soupe", "salade", "poulet",
            "boeuf", "porc", "poisson", "riz", "pâtes", "chocolat", "dessert", "restaurant",
            "recipe", "cooking", "baking", "food", "chicken", "beef", "pasta", "cake",
            # Sport
            "football", "basketball", "tennis", "rugby", "natation", "cyclisme", "sport",
            "gym", "musculation", "fitness", "marathon", "soccer", "baseball", "hockey",
            "formule 1", "moto gp",
            # Musique / divertissement
            "chanson", "musique", "concert", "guitare", "piano", "batterie", "rock", "pop",
            "rap", "jazz", "musique classique", "album", "chanteur", "chanteuse",
            "music", "song", "guitar", "drum", "band", "concert", "festival",
            # Actualités / politique
            "président", "élection", "gouvernement", "ministre", "actualité", "journal",
            "news", "president", "election", "government", "minister",
            # Mode / beauté
            "robe", "chaussure", "maquillage", "coiffure", "mode", "vêtement", "sac",
            "dress", "shoes", "makeup", "fashion", "clothing", "bag",
            # Jardinage / bricolage
            "jardinage", "plante", "fleur", "potager", "bricolage", "outil", "peinture",
            "garden", "plant", "flower", "diy", "tool", "paint",
            # Animaux
            "chien", "chat", "oiseau", "poisson rouge", "hamster", "animal", "vétérinaire",
            "dog", "cat", "bird", "pet", "veterinary",
            # Voyages / tourisme
            "hôtel", "avion", "train", "vacances", "plage", "montagne", "visite", "tourisme",
            "hotel", "plane", "train", "beach", "mountain", "tourism",
            # Divers
            "météo", "horoscope", "crypto monnaie", "bitcoin", "nft",
            "weather", "horoscope", "cryptocurrency", "bitcoin", "nft",
        }

    def analyze_query(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        detected_languages = []
        for lang, synonyms in self.tech_synonyms.items():
            if any(kw in query_lower for kw in [lang] + synonyms):
                detected_languages.append(lang)
        intent = "general"
        for i, keywords in self.search_intents.items():
            if any(kw in query_lower for kw in keywords):
                intent = i
                break
        expanded_terms = []
        for term, syns in self.tech_synonyms.items():
            if term in query_lower:
                expanded_terms.extend(syns)
        expanded_terms = list(set(expanded_terms))
        return {
            "original_query": query,
            "detected_languages": list(set(detected_languages)),
            "detected_concepts": [],
            "estimated_difficulty": "intermediate",
            "is_technical_query": len(detected_languages) > 0,
            "intent": intent,
            "expanded_terms": expanded_terms,
        }

    def contains_non_informatics(self, query: str) -> bool:
        """
        Vérifie si la requête contient un mot clairement non informatique.
        """
        query_lower = query.lower()
        for word in self.NON_INFORMATICS_KEYWORDS:
            # Vérifier comme mot entier (\b) pour éviter "dress" dans "address"
            if re.search(r'\b' + re.escape(word) + r'\b', query_lower):
                return True
        return False

    def is_likely_informatics(self, query: str) -> bool:
        """
        Vérifie si la requête contient au moins un terme technique.
        On considère également les intentions (tutorial, error…) comme informatiques.
        """
        analysis = self.analyze_query(query)
        if analysis['detected_languages'] or analysis['intent'] != 'general':
            return True
        # Vérification supplémentaire sur les mots individuels
        query_lower = query.lower()
        for word in query_lower.split():
            for term, synonyms in self.tech_synonyms.items():
                if word == term or word in synonyms:
                    return True
        return False

class TechnicalDocumentRanker:
    def __init__(self):
        self.query_analyzer = TechnicalQueryAnalyzer()

    def calculate_technical_score(self, document: Dict, query_analysis: Dict) -> float:
        technical_metadata = document.get('technical_metadata', {})
        if not technical_metadata:
            return 0.3

        scores = {
            'language_match': 0.0,
            'concept_match': 0.0,
            'difficulty_match': 0.0,
            'code_quality': 0.0,
            'pagerank': 0.0,
            'freshness': 0.0,
            'content_length': 0.0,
        }

        doc_langs = technical_metadata.get('programming_languages', [])
        query_langs = query_analysis.get('detected_languages', [])
        if query_langs:
            matches = sum(1 for lang in query_langs if any(lang.lower() == dlang.lower() for dlang in doc_langs))
            scores['language_match'] = matches / len(query_langs)
        else:
            scores['language_match'] = 0.5

        doc_concepts = technical_metadata.get('technical_concepts', [])
        query_concepts = query_analysis.get('detected_concepts', [])
        if query_concepts:
            matches = sum(1 for c in query_concepts if c in doc_concepts)
            scores['concept_match'] = matches / len(query_concepts)
        else:
            scores['concept_match'] = 0.5

        doc_difficulty = technical_metadata.get('difficulty_level', 'intermediate')
        query_difficulty = query_analysis.get('estimated_difficulty', 'intermediate')
        diff_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        doc_diff = diff_map.get(doc_difficulty, 2)
        query_diff = diff_map.get(query_difficulty, 2)
        scores['difficulty_match'] = 1.0 - abs(doc_diff - query_diff) / 2.0

        code_score = 0.0
        if technical_metadata.get('has_code_examples'):
            code_score += 0.8
        if technical_metadata.get('has_shell_commands'):
            code_score += 0.9
        scores['code_quality'] = min(1.0, code_score / 1.7)

        pagerank_val = document.get('pagerank')
        if pagerank_val is None:
            pagerank_val = 0.1
        scores['pagerank'] = min(1.0, pagerank_val)

        crawled_at = document.get('crawled_at')
        if crawled_at:
            try:
                from datetime import datetime
                days = (datetime.utcnow() - datetime.fromisoformat(crawled_at.replace('Z', '+00:00'))).days
                if days < 30:
                    scores['freshness'] = 1.0
                elif days < 90:
                    scores['freshness'] = 0.8
                elif days < 365:
                    scores['freshness'] = 0.5
                else:
                    scores['freshness'] = 0.2
            except:
                scores['freshness'] = 0.5
        else:
            scores['freshness'] = 0.5

        content_len = len(document.get('content', ''))
        scores['content_length'] = min(1.0, content_len / 5000)

        weights = {
            'language_match': 0.20,
            'concept_match': 0.20,
            'difficulty_match': 0.15,
            'code_quality': 0.15,
            'pagerank': 0.10,
            'freshness': 0.10,
            'content_length': 0.10,
        }

        return sum(scores[key] * weights[key] for key in weights)

    def rank_documents(self, documents: List[Dict], query: str, use_hybrid: bool = True) -> List[Dict]:
        query_analysis = self.query_analyzer.analyze_query(query)
        scored_docs = []
        for doc in documents:
            es_score = doc.get('_score', 1.0)
            tech_score = self.calculate_technical_score(doc.get('_source', {}), query_analysis)
            if use_hybrid and query_analysis['is_technical_query']:
                hybrid_score = (tech_score * 0.7) + (es_score * 0.3)
                ranking_method = "hybrid_technical"
            else:
                hybrid_score = es_score
                ranking_method = "elasticsearch"
            doc['technical_score'] = round(tech_score, 3)
            doc['hybrid_score'] = round(hybrid_score, 3)
            doc['ranking_method'] = ranking_method
            doc['_sort_score'] = hybrid_score
            scored_docs.append(doc)
        scored_docs.sort(key=lambda x: x['_sort_score'], reverse=True)
        return scored_docs

def check_elasticsearch_connection() -> bool:
    try:
        response = requests.get(f"{ELASTICSEARCH_URL}/_cluster/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"ES connection error: {e}")
        return False

async def get_query_embedding(query: str) -> Optional[List[float]]:
    global http_session
    if http_session is None or http_session.closed:
        http_session = aiohttp.ClientSession()
    try:
        async with http_session.post(f"{NLP_SERVICE_URL}/embed", json={"text": query}, timeout=5) as resp:
            if resp.status == 200:
                data = await resp.json()
                embedding = data.get("embedding")
                if embedding:
                    logger.info(f"✅ Embedding obtenu (dim {len(embedding)})")
                    return embedding
                else:
                    logger.warning("Pas d'embedding dans la réponse NLP")
                    return None
            else:
                logger.error(f"NLP service error: {resp.status}")
                return None
    except asyncio.TimeoutError:
        logger.error("Timeout appel NLP service")
        return None
    except Exception as e:
        logger.exception(f"Erreur appel NLP: {e}")
        return None

async def get_pagerank_scores(urls: List[str]) -> Dict[str, float]:
    if not urls:
        return {}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{PAGERANK_SERVICE_URL}/batch", json={"urls": urls}, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    logger.error(f"PageRank service error: {resp.status}")
                    return {}
    except Exception as e:
        logger.exception(f"Erreur PageRank: {e}")
        return {}

def build_enhanced_query(query: str, query_analysis: Dict[str, Any],
                         content_type: str = "all",
                         programming_language: List[str] = None,
                         difficulty_level: str = None,
                         has_code_examples: bool = None,
                         file_type: str = None) -> Dict[str, Any]:
    all_terms = query.split() + query_analysis.get('expanded_terms', [])
    should_clauses = []

    should_clauses.append({
        "match_phrase": {
            "title": {
                "query": query,
                "boost": 5.0
            }
        }
    })
    should_clauses.append({
        "multi_match": {
            "query": query,
            "fields": ["title^3", "content^2", "description^1.5"],
            "fuzziness": "AUTO",
            "boost": 2.0
        }
    })
    # Ajout de match sur les termes étendus (synonymes)
    if query_analysis.get('expanded_terms'):
        for term in query_analysis['expanded_terms']:
            should_clauses.append({
                "match": {
                    "content": {
                        "query": term,
                        "boost": 1.5,
                        "fuzziness": "AUTO"
                    }
                }
            })

    # Boost supplémentaire si des langages techniques sont détectés dans la requête
    detected_langs = query_analysis.get('detected_languages', [])
    if detected_langs:
        for lang in detected_langs:
            # On booste les documents qui mentionnent ce langage dans leurs métadonnées ou dans le texte
            should_clauses.append({
                "multi_match": {
                    "query": lang,
                    "fields": ["technical_metadata.programming_languages^3", "content^1.5", "title^2"],
                    "boost": 2.0
                }
            })

    filters = []

    if content_type == "images":
        filters.append({"exists": {"field": "image_urls"}})
    elif content_type == "videos":
        filters.append({
            "bool": {
                "should": [
                    {"term": {"content_type": "video"}},
                    {"term": {"content_type": "youtube_video"}}
                ]
            }
        })
    elif content_type == "youtube_video":
        filters.append({"term": {"content_type": "youtube_video"}})
    elif content_type == "web":
        filters.append({
            "bool": {
                "must_not": [
                    {"exists": {"field": "image_urls"}},
                    {"exists": {"field": "video_urls"}}
                ]
            }
        })

    if programming_language:
        filters.append({"terms": {"technical_metadata.programming_languages.keyword": programming_language}})
    if difficulty_level:
        filters.append({"term": {"technical_metadata.difficulty_level.keyword": difficulty_level}})
    if has_code_examples is not None:
        filters.append({"term": {"technical_metadata.has_code_examples": has_code_examples}})
    if file_type:
        filters.append({"term": {"file_type": file_type}})

    query_body = {
        "query": {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1
            }
        }
    }
    if filters:
        query_body["query"]["bool"]["filter"] = filters
    return query_body

def extract_technical_facets(hits: List[Dict]) -> Dict[str, Any]:
    facets = {
        "programming_languages": Counter(),
        "difficulty_levels": Counter(),
        "has_code_examples": 0,
        "content_types": Counter(),
        "technical_concepts": Counter(),
    }
    for hit in hits:
        source = hit.get('_source', {})
        metadata = source.get('technical_metadata', {})
        for lang in metadata.get('programming_languages', []):
            facets["programming_languages"][lang] += 1
        difficulty = metadata.get('difficulty_level', 'unknown')
        facets["difficulty_levels"][difficulty] += 1
        if metadata.get('has_code_examples'):
            facets["has_code_examples"] += 1
        for concept in metadata.get('technical_concepts', [])[:5]:
            facets["technical_concepts"][concept] += 1
        if source.get('image_urls'):
            facets["content_types"]["image"] += 1
        elif source.get('video_urls') or source.get('content_type') in ('video', 'youtube_video'):
            facets["content_types"]["video"] += 1
        else:
            facets["content_types"]["web"] += 1
    for key in facets:
        if isinstance(facets[key], Counter):
            facets[key] = dict(facets[key].most_common(10))
    return facets

@app.get("/health")
async def health_check():
    es_ok = check_elasticsearch_connection()
    return {
        "status": "healthy" if es_ok else "unhealthy",
        "elasticsearch": "connected" if es_ok else "disconnected",
        "document_count": 0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

async def get_nlp_synonyms(query: str) -> List[str]:
    words = query.lower().split()
    stop_words = {'est', 'pas', 'sur', 'dans', 'une', 'des', 'les', 'aux', 'avec', 'pour', 'que', 'le', 'la', 'un'}
    significant = [w for w in words if len(w) > 2 and w not in stop_words]
    if not significant:
        return []

    synonyms = []
    words_to_fetch = []
    # Vérifier le cache Redis pour chaque mot
    for word in significant[:5]:
        if redis_client:
            try:
                cache_key = f"syn:{word}"
                cached = await redis_client.get(cache_key)
                if cached:
                    synonyms.extend(json.loads(cached))
                    continue
            except Exception as e:
                logger.warning(f"Erreur cache Redis: {e}")
        words_to_fetch.append(word)

    # Interroger le NLP pour les mots non cachés
    if words_to_fetch:
        async with aiohttp.ClientSession() as session:
            for word in words_to_fetch:
                try:
                    async with session.get(
                        f"{NLP_SERVICE_URL}/similar",
                        params={"word": word, "top_k": 3, "threshold": 0.5}
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            sim = data.get("similar", [])
                            synonyms.extend(sim)
                            # Mettre en cache pour 24h
                            if redis_client:
                                try:
                                    await redis_client.setex(f"syn:{word}", 86400, json.dumps(sim))
                                except:
                                    pass
                except Exception as e:
                    logger.warning(f"Erreur synonym NLP pour '{word}': {e}")

    unique = list(set(synonyms) - set(significant))
    if unique:
        logger.info(f" Synonymes NLP ajoutés : {unique}")
    return unique

@app.post("/search", response_model=SearchResponse)
async def search_post(request: SearchRequest):
    start_time = time.time()
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Requête vide")

    if not check_elasticsearch_connection():
        raise HTTPException(status_code=503, detail="Elasticsearch indisponible")

    try:
        logger.info(f"🔍 Recherche: '{request.query}' - Type: {request.content_type}")

        analyzer = TechnicalQueryAnalyzer()
        query_analysis = analyzer.analyze_query(request.query)
        logger.info(f"📊 Analyse: langues={query_analysis['detected_languages']}, intention={query_analysis['intent']}, technique={query_analysis['is_technical_query']}")

        # ----------------------------------------------------------------
        # Nouvelle vérification : message hors domaine
        # ----------------------------------------------------------------
        if analyzer.contains_non_informatics(request.query) and not query_analysis['is_technical_query']:
            logger.info(f"Requête hors domaine (non‑informatique) : {request.query}")
            return SearchResponse(
                results=[],
                total=0,
                query=request.query,
                processing_time=0.0,
                page=1,
                total_pages=0,
                content_type=request.content_type,
                is_informatics_domain=False,
                domain_message="Votre recherche ne semble pas concerner le domaine informatique. Essayez avec des termes comme Python, Docker, machine learning, ou parcourez notre documentation.",
                technical_facets=None,
                ranking_method="none"
            )

        query_embedding = await get_query_embedding(request.query)
        if query_embedding:
            logger.info("✅ Recherche hybride activée (texte + vecteurs)")
        else:
            logger.info("ℹ️ Recherche textuelle seule (NLP indisponible)")

        es_query_body = build_enhanced_query(
            request.query, query_analysis,
            request.content_type, request.programming_language,
            request.difficulty_level, request.has_code_examples,
            request.file_type
        )

        # Augmentation du boost vectoriel pour donner plus de poids à la similarité sémantique
        VECTOR_BOOST = 3.0

        if query_embedding:
            hybrid_query = {
                "query": {
                    "bool": {
                        "should": [
                            es_query_body["query"],
                            {
                                "script_score": {
                                    "query": {"exists": {"field": "embedding"}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                        "params": {"query_vector": query_embedding}
                                    },
                                    "boost": VECTOR_BOOST
                                }
                            }
                        ],
                        "minimum_should_match": 1
                    }
                }
            }
            if "filter" in es_query_body["query"]["bool"]:
                hybrid_query["query"]["bool"]["filter"] = es_query_body["query"]["bool"]["filter"]
            final_query = hybrid_query
        else:
            final_query = es_query_body

        size_param = request.size * 2
        final_query["size"] = size_param
        final_query["highlight"] = {
            "fields": {
                "content": {"fragment_size": 150, "number_of_fragments": 1},
                "title": {"fragment_size": 100, "number_of_fragments": 1}
            }
        }

        # Ajout du suggester pour correction orthographique
        final_query["suggest"] = {
            "query_suggestion": {
                "text": request.query,
                "term": {"field": "content", "suggest_mode": "missing", "max_edits": 2}
            }
        }

        logger.debug(f"ES query: {json.dumps(final_query, default=str)}")
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search",
            json=final_query,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code != 200:
            logger.error(f"ES error: {response.text}")
            raise HTTPException(status_code=500, detail="Erreur Elasticsearch")

        data = response.json()
        hits = data.get('hits', {}).get('hits', [])
        total = data.get('hits', {}).get('total', {}).get('value', 0)

        # Extraction des suggestions
        suggestions = []
        suggest_data = data.get('suggest', {}).get('query_suggestion', [])
        if suggest_data:
            for option in suggest_data[0].get('options', []):
                suggestions.append(option['text'])

        urls = [hit['_source'].get('url') for hit in hits if hit.get('_source', {}).get('url')]
        pagerank_scores = await get_pagerank_scores(urls)
        for hit in hits:
            url = hit['_source'].get('url')
            if url in pagerank_scores:
                hit['_source']['pagerank'] = pagerank_scores[url]
            else:
                hit['_source']['pagerank'] = 0.1

        # ========== RERANKING AVEC CROSS-ENCODER ==========
        if cross_encoder is not None:
            try:
                top_n = min(50, len(hits))
                if top_n > 0:
                    top_hits = hits[:top_n]
                    pairs = [[request.query, hit['_source'].get('content', '')] for hit in top_hits]
                    scores = cross_encoder.predict(pairs)
                    for i, score in enumerate(scores):
                        top_hits[i]['_score'] = float(score)
                    top_hits.sort(key=lambda x: x['_score'], reverse=True)
                    hits = top_hits + hits[top_n:]
                    logger.info(f"Reranking appliqué sur {top_n} résultats")
            except Exception as e:
                logger.warning(f"Erreur lors du reranking: {e}")
        # ====================================================

        technical_ranker = TechnicalDocumentRanker()
        if query_analysis['is_technical_query']:
            hits = technical_ranker.rank_documents(hits, request.query, use_hybrid=True)
            ranking_method = "hybrid_technical"
        else:
            ranking_method = "elasticsearch"

        start = (request.page - 1) * request.size
        end = start + request.size
        paginated_hits = hits[start:end]

        results = []
        for hit in paginated_hits:
            source = hit.get('_source', {})
            highlight = hit.get('highlight', {})
            technical_metadata = source.get('technical_metadata', {})
            url = source.get('url', '')

            content_type = source.get('content_type', 'web')
            thumbnail = None
            duration = None
            views = None
            source_platform = None
            quality = None
            rating = None
            tags = []

            if content_type == 'youtube_video' and 'youtube_metadata' in source:
                yt = source['youtube_metadata']
                thumbnail = yt.get('thumbnail') or yt.get('default_thumbnail')
                duration = yt.get('duration_seconds')
                views = yt.get('view_count')
                source_platform = 'YouTube'
                tags = yt.get('tags', [])
                if not source.get('title'):
                    source['title'] = yt.get('title', 'Sans titre')
            else:
                videos_list = source.get('videos', [])
                if videos_list:
                    content_type = "video"
                    first_video = videos_list[0]
                    thumbnail = first_video.get('thumbnail')
                    duration = first_video.get('duration')
                    views = first_video.get('views')
                    source_platform = first_video.get('platform')
                    tags = source.get('keywords_found', [])[:5]
                    quality = "HD"
                    rating = 0.0
                elif source.get('video_urls'):
                    content_type = "video"
                    first_url = source['video_urls'][0]
                    if 'youtube' in first_url.lower() or 'youtu.be' in first_url.lower():
                        vid = re.search(r'(?:youtube\.com/(?:watch\?v=|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})', first_url)
                        if vid:
                            thumbnail = f"https://img.youtube.com/vi/{vid.group(1)}/hqdefault.jpg"
                    source_platform = source.get('domain')
                    tags = source.get('keywords_found', [])[:5]
                elif source.get('image_urls'):
                    content_type = "image"
                    thumbnail = source['image_urls'][0]
                elif source.get('file_type') == 'pdf':
                    content_type = "pdf"

            download_url = url
            if source.get('file_type') == 'pdf':
                download_url = source.get('original_file_url') or source.get('url')
                if download_url and 'minio:9000' in download_url:
                    minio_public = os.getenv('MINIO_PUBLIC_URL', 'http://localhost:9000')
                    download_url = download_url.replace('http://minio:9000', minio_public)

            snippet = source.get('snippet', '')
            if not snippet:
                if highlight.get('content'):
                    snippet = highlight['content'][0]
                elif highlight.get('title'):
                    snippet = highlight['title'][0]
                else:
                    content_text = source.get('content', '')
                    snippet = content_text[:150] + "..." if len(content_text) > 150 else content_text

            result = {
                "id": hit.get('_id'),
                "title": source.get('title', 'Sans titre'),
                "url": download_url,
                "domain": source.get('domain', 'unknown'),
                "snippet": snippet,
                "score": round(hit.get('_score', 0), 3),
                "content_type": content_type,
                "thumbnail": thumbnail,
                "duration": duration,
                "views": views,
                "source": source_platform,
                "quality": quality,
                "rating": rating,
                "tags": tags,
                "technical_info": {
                    "programming_languages": technical_metadata.get('programming_languages', []),
                    "difficulty_level": technical_metadata.get('difficulty_level', 'unknown'),
                    "has_code_examples": technical_metadata.get('has_code_examples', False),
                    "technical_score": hit.get('technical_score', 0),
                },
                "ranking_method": hit.get('ranking_method', ranking_method)
            }
            results.append(result)

        technical_facets = extract_technical_facets(hits)

        processing_time = time.time() - start_time
        total_pages = (total + request.size - 1) // request.size if total > 0 else 0

        logger.info(f"✅ Recherche terminée: {len(results)} résultats en {processing_time:.3f}s - méthode {ranking_method}")

        return SearchResponse(
            results=results,
            total=total,
            query=request.query,
            processing_time=round(processing_time, 3),
            page=request.page,
            total_pages=total_pages,
            content_type=request.content_type,
            suggestions=suggestions if suggestions else None,
            technical_facets=technical_facets,
            ranking_method=ranking_method
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Erreur recherche non gérée: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/search")
async def search_get(
    q: str = Query(...),
    size: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    content_type: str = Query("all"),
    programming_language: Optional[str] = Query(None),
    difficulty_level: Optional[str] = Query(None),
    has_code_examples: Optional[bool] = Query(None),
    platforms: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None)
):
    prog_lang_list = [lang.strip() for lang in programming_language.split(',')] if programming_language else None
    platform_list = [p.strip() for p in platforms.split(',')] if platforms else None
    request = SearchRequest(
        query=q, size=size, page=page, content_type=content_type,
        programming_language=prog_lang_list, difficulty_level=difficulty_level,
        has_code_examples=has_code_examples, platforms=platform_list, file_type=file_type
    )
    return await search_post(request)

@app.on_event("startup")
async def startup_event():
    global http_session
    http_session = aiohttp.ClientSession()
    logger.info("🚀 Search Service démarré avec support NLP et PageRank")
    global redis_client
    try:
        redis_client = redis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Connexion Redis établie")
    except Exception as e:
        logger.warning(f"⚠️ Redis indisponible: {e}")
        redis_client = None
    embedding = await get_query_embedding("test")
    if embedding:
        logger.info("✅ Connexion au NLP service établie")
    else:
        logger.warning("⚠️ Connexion au NLP service échouée, recherche vectorielle désactivée")

@app.on_event("shutdown")
async def shutdown_event():
    global http_session
    if http_session and not http_session.closed:
        await http_session.close()
        logger.info("Session HTTP fermée")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)