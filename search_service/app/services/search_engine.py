# app/services/search_engine.py
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ElasticsearchException
from typing import List, Dict, Optional, Any
import json
import time
from datetime import datetime
from models.schemas import SearchRequest, SearchResponse, SearchResult
from core.config import settings
from utils.metrics import record_search_time, measure_elasticsearch_latency
from core.logging import log_execution_time
import logging
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# Métriques détaillées
SEARCH_QUERIES = Counter(
    'search_queries_total',
    'Total des requêtes de recherche',
    ['query_type', 'domain', 'status']
)

SEARCH_LATENCY = Histogram(
    'search_latency_seconds',
    'Latence des recherches',
    ['query_type', 'domain']
)

ELASTICSEARCH_ERRORS = Counter(
    'elasticsearch_errors_total',
    'Erreurs Elasticsearch',
    ['error_type', 'operation']
)

class AdvancedSearchEngine:
    """
    Moteur de recherche avancé avec résilience et monitoring
    """
    
    def __init__(self, es_client: AsyncElasticsearch):
        self.es = es_client
        self.index_name = getattr(settings, "ELASTICSEARCH_INDEX", "tech_docs")
        self.settings = self._get_index_settings()
        self.mappings = self._get_index_mappings()
        
    def _get_index_settings(self) -> Dict[str, Any]:
        """Retourne les settings optimisés pour l'index"""
        return {
            "analysis": {
                "analyzer": {
                    "french_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "french_elision",
                            "french_stop",
                            "french_stemmer"
                        ]
                    },
                    "tech_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "tech_synonyms"
                        ]
                    }
                },
                "filter": {
                    "french_stop": {
                        "type": "stop",
                        "stopwords": "_french_"
                    },
                    "french_stemmer": {
                        "type": "stemmer",
                        "language": "french"
                    },
                    "french_elision": {
                        "type": "elision",
                        "articles": ["l", "m", "t", "qu", "n", "s", "j", "d"]
                    },
                    "tech_synonyms": {
                        "type": "synonym",
                        "synonyms": [
                            "ai, artificial intelligence, machine intelligence",
                            "ml, machine learning",
                            "db, database, databases",
                            "api, application programming interface",
                            "ui, user interface",
                            "ux, user experience"
                        ]
                    }
                }
            }
        }
    
    def _get_index_mappings(self) -> Dict[str, Any]:
        """Retourne les mappings avancés pour l'index"""
        return {
            "dynamic": "strict",
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "french_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword"},
                        "stemmed": {"type": "text", "analyzer": "french_analyzer"}
                    }
                },
                "content": {
                    "type": "text", 
                    "analyzer": "french_analyzer",
                    "fields": {
                        "tech": {"type": "text", "analyzer": "tech_analyzer"}
                    }
                },
                "url": {"type": "keyword"},
                "domain": {
                    "type": "keyword",
                    "fields": {
                        "text": {"type": "text"}
                    }
                },
                "content_type": {"type": "keyword"},
                "keywords": {
                    "type": "text",
                    "analyzer": "tech_analyzer"
                },
                "description": {"type": "text"},
                "author": {"type": "keyword"},
                "published_date": {"type": "date"},
                "last_updated": {"type": "date"},
                "page_rank": {"type": "float"},
                "popularity": {"type": "float"},
                "quality_score": {"type": "float"},
                "technical_level": {
                    "type": "keyword",
                    "fields": {
                        "rank": {
                            "type": "integer",
                            "coerce": True
                        }
                    }
                },
                "metadata": {
                    "type": "object",
                    "dynamic": True
                },
                "vector_embedding": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    
    @log_execution_time({"component": "search_engine", "operation": "search"})
    async def search(self, request: SearchRequest) -> SearchResponse:
        """
        Execute une recherche avancée avec tous les features
        """
        SEARCH_QUERIES.labels(
            query_type="standard",
            domain=request.filters.get('domain', 'unknown'),
            status="started"
        ).inc()
        
        try:
            # Construction de la requête Elasticsearch avancée
            es_query = self._build_advanced_query(request)
            
            # Recherche dans Elasticsearch avec monitoring
            start_time = time.time()
            es_response = await measure_elasticsearch_latency(
                self.es.search,
                index=self.index_name,
                body=es_query,
                size=request.size,
                from_=request.from_,
                request_timeout=settings.SEARCH_TIMEOUT
            )
            search_time = time.time() - start_time
            
            # Transformation des résultats
            results = self._transform_results(es_response, request.query)
            
            # Métriques de succès
            SEARCH_QUERIES.labels(
                query_type="standard", 
                domain=request.filters.get('domain', 'unknown'),
                status="success"
            ).inc()
            
            SEARCH_LATENCY.labels(
                query_type="standard",
                domain=request.filters.get('domain', 'unknown')
            ).observe(search_time)
            
            return SearchResponse(
                query=request.query,
                results=results,
                total_hits=es_response['hits']['total']['value'],
                search_time=search_time,
                page=request.page,
                total_pages=(es_response['hits']['total']['value'] + request.size - 1) // request.size,
                facets=self._extract_facets(es_response),
                suggestions=self._generate_suggestions(request.query, results)
            )
            
        except ElasticsearchException as e:
            # Métriques d'erreur
            SEARCH_QUERIES.labels(
                query_type="standard",
                domain=request.filters.get('domain', 'unknown'),
                status="error"
            ).inc()
            
            ELASTICSEARCH_ERRORS.labels(
                error_type=type(e).__name__,
                operation="search"
            ).inc()
            
            logger.error(f"Elasticsearch error during search: {str(e)}")
            raise
    
    def _build_advanced_query(self, request: SearchRequest) -> Dict[str, Any]:
        """Construit une requête Elasticsearch avancée avec multiples stratégies"""
        
        # Query principale avec multiple strategies
        main_query = {
            "bool": {
                "should": [
                    # 1. Recherche phrase exacte (boost élevé)
                    {
                        "match_phrase": {
                            "content": {
                                "query": request.query,
                                "boost": 3.0
                            }
                        }
                    },
                    # 2. Recherche multi-champs avec boosts
                    {
                        "multi_match": {
                            "query": request.query,
                            "fields": [
                                "title^3.0",
                                "content^2.0", 
                                "keywords^2.5",
                                "description^1.5",
                                "content.tech^1.2",
                                "domain.text^0.8"
                            ],
                            "type": "best_fields",
                            "fuzziness": "AUTO",
                            "operator": "and",
                            "boost": 2.0
                        }
                    },
                    # 3. Recherche avec synonymes techniques
                    {
                        "multi_match": {
                            "query": request.query,
                            "fields": ["keywords", "content.tech"],
                            "type": "cross_fields",
                            "boost": 1.5
                        }
                    },
                    # 4. Recherche partielle (prefix/wildcard)
                    {
                        "bool": {
                            "should": [
                                {
                                    "prefix": {
                                        "title": {
                                            "value": request.query.lower(),
                                            "boost": 0.5
                                        }
                                    }
                                },
                                {
                                    "wildcard": {
                                        "content": {
                                            "value": f"*{request.query}*",
                                            "boost": 0.3
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ],
                "minimum_should_match": 1,
                "filter": []
            }
        }
        
        # Application des filtres
        if request.filters:
            self._apply_advanced_filters(main_query, request.filters)
        
        # Construction de la requête complète
        es_query = {
            "query": main_query,
            "highlight": self._get_highlight_config(),
            "aggs": self._get_aggregations_config(),
            "sort": self._get_sort_config(request),
            "suggest": self._get_suggest_config(request.query),
            "rescore": self._get_rescore_config(request.query),
            "track_total_hits": True,
            "timeout": f"{settings.SEARCH_TIMEOUT}s"
        }
        
        return es_query
    
    def _apply_advanced_filters(self, query: Dict, filters: Dict):
        """Applique des filtres avancés à la requête"""
        bool_query = query["bool"]
        
        # Filtre par domaine
        if filters.get('domains'):
            bool_query["filter"].append({
                "terms": {"domain": filters['domains']}
            })
        
        # Filtre par type de contenu
        if filters.get('content_types'):
            bool_query["filter"].append({
                "terms": {"content_type": filters['content_types']}
            })
        
        # Filtre par date
        if filters.get('date_range'):
            bool_query["filter"].append({
                "range": {
                    "published_date": {
                        "gte": filters['date_range'].get('start'),
                        "lte": filters['date_range'].get('end'),
                        "format": "yyyy-MM-dd"
                    }
                }
            })
        
        # Filtre par niveau technique
        if filters.get('technical_level'):
            bool_query["filter"].append({
                "terms": {"technical_level": filters['technical_level']}
            })
        
        # Filtre par score minimum
        if filters.get('min_page_rank'):
            bool_query["filter"].append({
                "range": {
                    "page_rank": {
                        "gte": filters['min_page_rank']
                    }
                }
            })
        
        # Filtre par qualité
        if filters.get('min_quality'):
            bool_query["filter"].append({
                "range": {
                    "quality_score": {
                        "gte": filters['min_quality']
                    }
                }
            })
    
    def _get_highlight_config(self) -> Dict:
        """Configuration avancée du highlighting"""
        return {
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
            "fields": {
                "title": {
                    "number_of_fragments": 0,
                    "highlight_query": {
                        "match": {"title": {"query": "{query}"}}
                    }
                },
                "content": {
                    "fragment_size": 150,
                    "number_of_fragments": 3,
                    "type": "fvh",
                    "boundary_scanner": "sentence"
                },
                "description": {
                    "number_of_fragments": 1,
                    "fragment_size": 100
                }
            }
        }
    
    def _get_aggregations_config(self) -> Dict:
        """Configuration des agrégations pour les facettes"""
        return {
            "domains": {
                "terms": {
                    "field": "domain",
                    "size": 10,
                    "order": {"_count": "desc"}
                }
            },
            "content_types": {
                "terms": {
                    "field": "content_type", 
                    "size": 5
                }
            },
            "technical_levels": {
                "terms": {
                    "field": "technical_level"
                }
            },
            "date_histogram": {
                "date_histogram": {
                    "field": "published_date",
                    "calendar_interval": "month",
                    "format": "yyyy-MM"
                }
            },
            "quality_ranges": {
                "range": {
                    "field": "quality_score",
                    "ranges": [
                        {"to": 0.3},
                        {"from": 0.3, "to": 0.7},
                        {"from": 0.7}
                    ]
                }
            }
        }
    
    def _get_sort_config(self, request: SearchRequest) -> List[Dict]:
        """Configuration du tri des résultats"""
        sort_field = request.sort_by or "relevance"
        
        sort_configs = {
            "relevance": [
                {"_score": {"order": "desc"}},
                {"page_rank": {"order": "desc"}},
                {"published_date": {"order": "desc"}}
            ],
            "date": [
                {"published_date": {"order": "desc"}},
                {"_score": {"order": "desc"}}
            ],
            "popularity": [
                {"page_rank": {"order": "desc"}},
                {"_score": {"order": "desc"}}
            ],
            "quality": [
                {"quality_score": {"order": "desc"}},
                {"_score": {"order": "desc"}}
            ]
        }
        
        return sort_configs.get(sort_field, sort_configs["relevance"])
    
    def _get_suggest_config(self, query: str) -> Dict:
        """Configuration de la suggestion de requêtes"""
        return {
            "query_suggestion": {
                "text": query,
                "term": {
                    "field": "content",
                    "suggest_mode": "missing",
                    "max_edits": 2
                }
            }
        }
    
    def _get_rescore_config(self, query: str) -> List[Dict]:
        """Configuration du rescoring pour améliorer la pertinence"""
        return [
            {
                "window_size": 100,
                "query": {
                    "rescore_query": {
                        "match_phrase": {
                            "content": {
                                "query": query,
                                "slop": 2
                            }
                        }
                    },
                    "query_weight": 0.7,
                    "rescore_query_weight": 1.2
                } 
            }
        ]
    
    def _transform_results(self, es_response: Dict, original_query: str) -> List[SearchResult]:
        """Transforme les résultats Elasticsearch en objets SearchResult enrichis"""
        results = []
        
        for hit in es_response['hits']['hits']:
            source = hit['_source']
            highlight = hit.get('highlight', {})
            
            # Extraction des métadonnées YouTube si présentes
            youtube_metadata = None
            if source.get('content_type') == 'youtube_video' and 'youtube_metadata' in source:
                yt = source['youtube_metadata']
                youtube_metadata = {
                    "title": yt.get("title"),
                    "description": yt.get("description"),
                    "tags": yt.get("tags", []),
                    "view_count": yt.get("view_count", 0),
                    "like_count": yt.get("like_count", 0),
                    "duration_seconds": yt.get("duration_seconds"),
                    "thumbnail": yt.get("thumbnail"),
                    "watch_url": yt.get("watch_url") or yt.get("url"),
                    "embed_url": yt.get("embed_url"),
                    "channel_title": yt.get("channel_title"),
                    "published_at": yt.get("published_at"),
                }
                # Surcharge du titre si nécessaire
                if not source.get('title') or source.get('title') == 'YouTube':
                    source['title'] = yt.get('title', source.get('title', ''))
            
            result = SearchResult(
                id=hit['_id'],
                title=source.get('title', ''),
                url=source.get('url', ''),
                description=source.get('description', ''),
                content_snippet=self._extract_optimal_snippet(highlight, source, original_query),
                domain=source.get('domain', ''),
                content_type=source.get('content_type', ''),
                published_date=source.get('published_date'),
                page_rank=source.get('page_rank', 0.0),
                relevance_score=hit['_score'],
                rank=len(results) + 1,
                highlights=highlight,
                # pas de author, technical_level, quality_score dans ton SearchResult actuel
                youtube_metadata=youtube_metadata
            )
            results.append(result)
        
        return results
    
    def _extract_optimal_snippet(self, highlight: Dict, source: Dict, query: str) -> str:
        """Extrait le snippet optimal en utilisant les highlights ou le contenu"""
        # Priorité 1: Highlights du contenu
        if highlight.get('content'):
            best_snippet = self._select_best_highlight(highlight['content'], query)
            if best_snippet:
                return best_snippet
        
        # Priorité 2: Highlight du titre
        if highlight.get('title'):
            return highlight['title'][0]
        
        # Priorité 3: Description
        if source.get('description'):
            return source['description'][:200] + '...'
        
        # Priorité 4: Extrait intelligent du contenu
        content = source.get('content', '')
        return self._extract_relevant_snippet(content, query)
    
    def _select_best_highlight(self, highlights: List[str], query: str) -> Optional[str]:
        """Sélectionne le meilleur highlight basé sur la requête"""
        if not highlights:
            return None
        
        # Simple stratégie: prendre le premier highlight avec le plus de termes de la requête
        query_terms = set(query.lower().split())
        best_highlight = highlights[0]
        max_matches = 0
        
        for highlight in highlights:
            highlight_terms = set(highlight.lower().split())
            matches = len(query_terms.intersection(highlight_terms))
            if matches > max_matches:
                max_matches = matches
                best_highlight = highlight
        
        return best_highlight
    
    def _extract_relevant_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Extrait un snippet pertinent du contenu basé sur la requête"""
        if not content:
            return ""
        
        query_terms = query.lower().split()
        content_lower = content.lower()
        
        # Trouver la première occurrence d'un terme de la requête
        for term in query_terms:
            if len(term) > 3:  # Ignorer les termes trop courts
                pos = content_lower.find(term)
                if pos != -1:
                    start = max(0, pos - 50)
                    end = min(len(content), start + max_length)
                    snippet = content[start:end]
                    
                    # S'assurer que le snippet se termine sur un mot complet
                    if end < len(content):
                        last_space = snippet.rfind(' ')
                        if last_space != -1:
                            snippet = snippet[:last_space]
                    
                    return snippet + '...'
        
        # Fallback: début du contenu
        return content[:max_length] + '...'
    
    def _extract_facets(self, es_response: Dict) -> Dict[str, Any]:
        """Extrait les facettes des agrégations"""
        aggs = es_response.get('aggregations', {})
        
        return {
            'domains': [
                {'key': bucket['key'], 'count': bucket['doc_count']}
                for bucket in aggs.get('domains', {}).get('buckets', [])
            ],
            'content_types': [
                {'key': bucket['key'], 'count': bucket['doc_count']}
                for bucket in aggs.get('content_types', {}).get('buckets', [])
            ],
            'technical_levels': [
                {'key': bucket['key'], 'count': bucket['doc_count']}
                for bucket in aggs.get('technical_levels', {}).get('buckets', [])
            ]
        }
    
    def _generate_suggestions(self, query: str, results: List[SearchResult]) -> List[str]:
        """Génère des suggestions basées sur les résultats et la requête"""
        suggestions = []
        
        # Suggestion de correction d'orthographe
        if len(results) < 3:
            suggestions.append("Vérifiez l'orthographe de votre recherche")
        
        # Suggestion de termes liés
        unique_domains = set(result.domain for result in results[:5])
        if unique_domains:
            suggestions.append(f"Domaines trouvés: {', '.join(list(unique_domains)[:3])}")
        
        return suggestions
    
    @log_execution_time({"component": "search_engine", "operation": "autocomplete"})
    async def autocomplete(self, prefix: str, size: int = 10, user_context: Dict = None) -> List[str]:
        """Suggestion automatique avancée avec contexte utilisateur"""
        try:
            # Recherche dans l'index de suggestions
            response = await self.es.search(
                index="query_suggestions",
                body={
                    "suggest": {
                        "query_suggest": {
                            "prefix": prefix,
                            "completion": {
                                "field": "suggest",
                                "size": size,
                                "fuzzy": {
                                    "fuzziness": 1,
                                    "prefix_length": 2
                                },
                                "contexts": user_context or {}
                            }
                        }
                    }
                }
            )
            
            suggestions = []
            for option in response['suggest']['query_suggest'][0]['options']:
                suggestions.append(option['text'])
            
            return suggestions
            
        except ElasticsearchException as e:
            logger.warning(f"Autocomplete failed, falling back to simple prefix: {str(e)}")
            # Fallback simple
            return [f"{prefix} programmation", f"{prefix} python", f"{prefix} tutoriel"]
    
    @log_execution_time({"component": "search_engine", "operation": "more_like_this"})
    async def more_like_this(self, doc_id: str, size: int = 5, fields: List[str] = None) -> List[SearchResult]:
        """Trouve des documents similaires avec configuration avancée"""
        if fields is None:
            fields = ["title", "content", "keywords", "description"]
        
        try:
            response = await self.es.search(
                index=self.index_name,
                body={
                    "query": {
                        "more_like_this": {
                            "fields": fields,
                            "like": [{"_id": doc_id}],
                            "min_term_freq": 1,
                            "max_query_terms": 25,
                            "min_doc_freq": 1,
                            "max_doc_freq": 1000,
                            "min_word_length": 3,
                            "boost_terms": 1.0,
                            "include": True
                        }
                    },
                    "size": size
                }
            )
            
            return self._transform_results(response, "similar documents")
            
        except ElasticsearchException as e:
            logger.error(f"More-like-this search failed: {str(e)}")
            return []
    
    async def check_health(self) -> Dict[str, Any]:
        """Vérifie la santé d'Elasticsearch et de l'index"""
        try:
            # Vérifier la connexion
            cluster_health = await self.es.cluster.health()
            index_stats = await self.es.indices.stats(index=self.index_name)
            
            return {
                "status": "healthy",
                "cluster_status": cluster_health.get('status'),
                "number_of_nodes": cluster_health.get('number_of_nodes'),
                "active_shards": cluster_health.get('active_shards'),
                "document_count": index_stats['indices'][self.index_name]['total']['docs']['count'],
                "index_size": index_stats['indices'][self.index_name]['total']['store']['size_in_bytes']
            }
            
        except ElasticsearchException as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }