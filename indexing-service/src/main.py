import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urlparse
from datetime import datetime
from src.processors.media_processor import process_videos_data
from fastapi import FastAPI
from elasticsearch import Elasticsearch
from aiokafka.structs import ConsumerRecord

from src.config import settings
from src.processors.async_kafka_consumer import AIOConsumer
from src.processors.elasticsearch_indexer import get_es_client_with_retry, index_documents_bulk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("indexing-service.main")

# ==================== VARIABLES GLOBALES POUR MAINTENIR LE CONSUMER ====================
kafka_consumer = None
kafka_consumer_task = None

# ==================== DOCUMENT TRANSFORMATION ====================

def transform_document_to_compatible_format(doc):
    """Transforme le document du format Kafka vers le format compatible Elasticsearch"""
    
    # NOUVEAU: Format avec médias
    if 'image_urls' in doc or 'videos' in doc:  # ← CHANGÉ: 'videos' au lieu de 'video_urls'
        source_url = doc.get('url', '')
        domain = urlparse(source_url).netloc if source_url else ""
        
        # Déterminer le contenu principal
        content = doc.get('extracted_content', '')
        if not content:
            content = doc.get('body', '')[:10000]

        # EXTRAIRE LES URLs VIDÉOS DES DONNÉES STRUCTURÉES
        video_urls = []
        videos_data = doc.get('videos', [])
        
        for video in videos_data:
            if isinstance(video, dict):
                # Extraire toutes les URLs possibles des vidéos
                for key in ['embed_url', 'watch_url', 'video_url', 'thumbnail']:
                    url = video.get(key)
                    if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
                        video_urls.append(url)
        
        return {
            "url": source_url,
            "response_url": source_url,
            "title": doc.get('title', ''),
            "description": doc.get('description', ''),
            "body": doc.get('body', ''),
            "content": content,
            "extracted_content": doc.get('extracted_content', ''),
            "domain": domain,
            "keywords_found": doc.get('keywords_found', []),
            "status_code": doc.get('status_code', 200),
            "appid": doc.get('appid', 'default'),
            "crawlid": doc.get('crawlid', 'unknown'),
            
            # ✅ CORRECTION CRITIQUE ICI :
            "image_urls": doc.get('image_urls', []),
            "videos": doc.get('videos', []),  # ← DONNÉES STRUCTURÉES COMPLÈTES
            "video_urls": video_urls,  # ← URLs EXTRACTIES DES VIDÉOS
            "media_count": doc.get('media_count', 0),
            "content_type": doc.get('content_type', 'text'),
            "crawled_at": doc.get('crawled_at', datetime.utcnow().isoformat()),
            
            "links": doc.get('links', []),
            "metadata": {
                "title": doc.get('title', 'Titre non disponible'),
                "url": source_url,
                "source": source_url,
                "content_type": "text/html",
                "language": "fr",
                "word_count": len(content.split()),
                "source_format": "scrapy_cluster_with_media",
                "appid": doc.get('appid', 'default'),
                "crawlid": doc.get('crawlid', 'unknown'),
                "media_summary": {
                    "images_count": len(doc.get('image_urls', [])),
                    "videos_count": len(doc.get('videos', [])),  # ← CORRIGÉ
                    "content_type": doc.get('content_type', 'text')
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
            "pagerank": 0.1
        }

# ==================== KAFKA MESSAGE PARSING ====================

def parse_message_value(raw: Any) -> dict:
    """Transforme payload kafka -> document dict"""
    if isinstance(raw, bytes):
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {"raw": raw.decode("utf-8", errors="ignore")}
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw}
    if isinstance(raw, dict):
        return raw
    return {"raw": str(raw)}

# ==================== MESSAGE HANDLING ====================

async def handle_message(msg: ConsumerRecord):
    """Handler appelé pour chaque message Kafka"""
    try:
        # Parser le payload
        raw_doc = parse_message_value(msg.value)

        logger.info("📥 Kafka message received topic=%s partition=%s offset=%s", 
                    msg.topic, msg.partition, msg.offset)

        # Transformer le document vers le format compatible
        doc = transform_document_to_compatible_format(raw_doc)
        
        if doc is None:
            logger.warning("❌ Document transformation failed for offset=%s", msg.offset)
            return

        # Log des informations médias
        media_info = f"images:{len(doc.get('image_urls', []))} videos:{len(doc.get('video_urls', []))} type:{doc.get('content_type', 'text')}"
        logger.info("🔄 Transformed document: url=%s, title=%.50s, %s", 
                   doc.get('url', 'unknown'), doc.get('title', 'unknown'), media_info)

        # Indexer dans Elasticsearch
        es = app.state.es_client
        if es is None:
            logger.error("❌ Elasticsearch client not available, skipping message")
            return
            
        index_name = getattr(settings, "ES_INDEX", "tech_docs")
        
        # Indexer le document
        try:
            response = es.index(
                index=index_name,
                body=doc
            )
            logger.info("✅ Successfully indexed message offset=%s, _id=%s, %s", 
                       msg.offset, response.get('_id'), media_info)
            
        except Exception as e:
            logger.error("❌ Elasticsearch indexing failed for offset=%s: %s", msg.offset, str(e))
        
    except Exception as e:
        logger.exception("💥 Error processing message offset=%s: %s", msg.offset, str(e))

# ==================== ELASTICSEARCH MAPPING ====================

ELASTICSEARCH_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "french_analyzer": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "french_elision",
                        "french_stop",
                        "french_stemmer"
                    ]
                },
                "tech_keyword_analyzer": {
                    "type": "custom",
                    "tokenizer": "keyword",
                    "filter": ["lowercase"]
                },
                "code_analyzer": {
                    "type": "custom",
                    "tokenizer": "pattern",
                    "pattern": r"[^\w#@]+|(?<=[a-z])(?=[A-Z])",
                    "filter": ["lowercase"]
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
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            # Champs principaux avec boosts
            "title": {
                "type": "text",
                "analyzer": "french_analyzer",
                "fields": {
                    "keyword": {"type": "keyword", "ignore_above": 256},
                    "raw": {"type": "keyword"}
                },
                "boost": 3.0
            },
            "content": {
                "type": "text",
                "analyzer": "french_analyzer",
                "fields": {
                    "tech": {
                        "type": "text",
                        "analyzer": "code_analyzer"
                    },
                    "exact": {"type": "keyword"}
                },
                "boost": 2.0
            },
            "extracted_content": {
                "type": "text",
                "analyzer": "french_analyzer",
                "boost": 1.5
            },
            
            # Métadonnées techniques
            "url": {
                "type": "keyword",
                "doc_values": True
            },
            "domain": {
                "type": "keyword",
                "fields": {
                    "text": {"type": "text", "analyzer": "tech_keyword_analyzer"}
                }
            },
            "keywords_found": {
                "type": "keyword",
                "fields": {
                    "text": {"type": "text", "analyzer": "tech_keyword_analyzer"}
                }
            },
            
            # Champs pour le ranking
            "quality_score": {
                "type": "float",
                "null_value": 0.5
            },
            "pagerank": {
                "type": "float",
                "null_value": 0.1
            },
            "popularity_score": {
                "type": "integer",
                "null_value": 1
            },
            "technical_level": {
                "type": "keyword"
            },
            
            # Dates
            "crawled_at": {"type": "date"},
            "last_updated": {"type": "date"},
            "timestamp": {"type": "date"},
            
            # Champs structurés
            "metadata": {
                "type": "object",
                "properties": {
                    "word_count": {"type": "integer"},
                    "language": {"type": "keyword"},
                    "source_type": {"type": "keyword"},
                    "has_code_examples": {"type": "boolean"},
                    "is_tutorial": {"type": "boolean"},
                    "is_api_doc": {"type": "boolean"}
                }
            },
            
            # Pour la recherche sémantique
            "embedding": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

# ==================== APPLICATION LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application - CORRIGÉE"""
    global kafka_consumer, kafka_consumer_task
    
    loop = asyncio.get_running_loop()

    # Désactiver le consumer Kafka si la variable d'environnement DISABLE_KAFKA est définie
    disable_kafka = os.getenv("DISABLE_KAFKA", "false").lower() == "true"

    # Configuration du client Elasticsearch avec mécanisme de réessai
    try:
        es_client: Elasticsearch = get_es_client_with_retry(
            hosts=getattr(settings, "ES_HOSTS", None),
            user=getattr(settings, "ES_USER", None),
            password=getattr(settings, "ES_PASSWORD", None),
            max_retries=10,
            retry_delay=5,
        )
        app.state.es_client = es_client
        logger.info("✅ Successfully connected to Elasticsearch")
    except Exception as e:
        logger.error("❌ Failed to connect to Elasticsearch: %s", str(e))
        app.state.es_client = None

    # Création de l'index avec le mapping complet (si le client ES est disponible)
    if app.state.es_client is not None:
        index_name = getattr(settings, "ES_INDEX", "tech_docs")
        try:
            if not app.state.es_client.indices.exists(index=index_name):
                app.state.es_client.indices.create(index=index_name, body=ELASTICSEARCH_MAPPING)
                logger.info("✅ Created index %s with COMPLETE MAPPING", index_name)
            else:
                logger.info("ℹ️ Index %s already exists", index_name)
        except Exception as e:
            logger.exception("❌ Error ensuring index exists: %s", str(e))
    else:
        logger.warning("⚠️ Skipping index creation: no Elasticsearch connection")

    # Configuration du consommateur Kafka - CORRECTION : maintenir le consumer en vie
    if not disable_kafka:
        try:
            kafka_config = {
                "bootstrap.servers": getattr(settings, "KAFKA_BROKERS"),
                "group.id": getattr(settings, "KAFKA_GROUP_ID", "indexer-group"),
                "auto.offset.reset": "earliest",
            }
            kafka_consumer = AIOConsumer(kafka_config, [getattr(settings, "KAFKA_TOPIC")], loop)
            
            # Démarrer la consommation en arrière-plan - SANS attendre
            kafka_consumer_task = loop.create_task(kafka_consumer.consume(handle_message))
            logger.info("✅ Kafka consumer started and running in background")
            
            # Attendre un peu pour que le consumer se connecte
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error("❌ Failed to start Kafka consumer: %s", str(e))
    else:
        logger.info("ℹ️ Kafka consumer disabled by DISABLE_KAFKA environment variable")

    yield  # L'application est en cours d'exécution - LE CONSUMER CONTINUE À TOURNER

    # Nettoyage à l'arrêt - SEULEMENT quand l'application s'arrête
    logger.info("🛑 Shutting down indexing service...")
    if kafka_consumer_task is not None:
        kafka_consumer_task.cancel()
        try:
            await kafka_consumer_task
        except asyncio.CancelledError:
            logger.info("✅ Kafka consumer task cancelled")
        except Exception as e:
            logger.error("❌ Error stopping consumer task: %s", str(e))
    
    if kafka_consumer is not None:
        try:
            await kafka_consumer.stop()
            logger.info("✅ Kafka consumer stopped!")
        except Exception as e:
            logger.error("❌ Error stopping consumer: %s", str(e))

# ==================== FASTAPI APPLICATION ====================

app = FastAPI(
    title="Indexing Service",
    description="Service d'indexation des documents crawlé dans Elasticsearch",
    version="1.0.0",
    lifespan=lifespan
)

# ==================== API ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Endpoint de santé du service"""
    health_status = {
        "status": "healthy",
        "service": "indexing",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        es = getattr(app.state, "es_client", None)
        if es is None:
            health_status["status"] = "unhealthy"
            health_status["elasticsearch"] = "not_connected"
            return health_status
        
        # Test de connexion Elasticsearch
        if not es.ping():
            health_status["status"] = "unhealthy"
            health_status["elasticsearch"] = "ping_failed"
        else:
            info = es.info()
            health_status["elasticsearch"] = {
                "cluster_name": info.get("cluster_name"),
                "status": "connected",
                "version": info.get("version", {}).get("number")
            }
            
            # Vérifier l'index
            index_name = getattr(settings, "ES_INDEX", "tech_docs")
            if es.indices.exists(index=index_name):
                count_result = es.count(index=index_name)
                health_status["index"] = {
                    "exists": True,
                    "document_count": count_result.get('count', 0)
                }
            else:
                health_status["index"] = {"exists": False}
                
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Indexing Service is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/stats")
async def get_stats():
    """Endpoint des statistiques"""
    stats = {
        "service": "indexing",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        es = getattr(app.state, "es_client", None)
        if es is not None:
            index_name = getattr(settings, "ES_INDEX", "tech_docs")
            if es.indices.exists(index=index_name):
                # Compter les documents
                count_result = es.count(index=index_name)
                stats["document_count"] = count_result.get('count', 0)
                
                # Informations sur l'index
                index_stats = es.indices.stats(index=index_name)
                stats["index_size"] = {
                    "docs": index_stats['_all']['primaries']['docs']['count'],
                    "size_in_bytes": index_stats['_all']['primaries']['store']['size_in_bytes']
                }
    except Exception as e:
        stats["error"] = str(e)
    
    return stats

@app.post("/index-manual")
async def index_manual_document(document: dict):
    """Endpoint pour indexer manuellement un document (pour les tests)"""
    try:
        # Transformer le document
        transformed_doc = transform_document_to_compatible_format(document)
        
        if transformed_doc is None:
            return {"status": "error", "message": "Document transformation failed"}
            
        # Indexer dans Elasticsearch
        es = app.state.es_client
        if es is None:
            return {"status": "error", "message": "Elasticsearch client not available"}
            
        index_name = getattr(settings, "ES_INDEX", "tech_docs")
        result = es.index(index=index_name, body=transformed_doc)
        
        return {
            "status": "success",
            "document_id": result.get('_id'),
            "message": "Document indexed successfully"
        }
        
    except Exception as e:
        logger.exception("Error in manual indexing")
        return {"status": "error", "message": str(e)}

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )