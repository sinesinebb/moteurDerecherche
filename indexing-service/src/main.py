# indexing-service/src/main.py
import asyncio
import json
import logging
import os
import signal
import re
import hashlib
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional
import aiohttp

from fastapi import FastAPI
from aiokafka.structs import ConsumerRecord

from src.config import settings
from src.processors.elasticsearch_indexer import (
    get_es_client_with_retry,
    index_documents_bulk,
)
from src.processors.nlp_processor import (
    embedding_from_text,  # on garde le fallback
    extract_text_from_raw_response,
    set_text_embedding_model,
)
from src.processors.metadata_enricher import enrich_metadata
from src.processors.media_processor import process_videos_data
from src.processors.html_cleaner import clean_html 

# Optional: allow injecting a sentence-transformers model via env path / import
# try:
#     if os.getenv("EMBEDDING_MODEL") == "sentence_transformers":
#         from sentence_transformers import SentenceTransformer
#         _m = SentenceTransformer(os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2"))
#         set_text_embedding_model(lambda s: _m.encode(s).tolist())
# except Exception:
#     pass

from src.processors.async_kafka_consumer import AIOConsumer
from src.processors.youtube_updater import update_youtube_metadata, mark_youtube_unavailable

logger = logging.getLogger("indexing-service.main")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

ES_INDEX = getattr(settings, "ES_INDEX", "tech_docs")
BATCH_SIZE = int(os.getenv("INDEX_BATCH_SIZE", "128"))
BATCH_INTERVAL = float(os.getenv("INDEX_BATCH_INTERVAL", "2.0"))
# EMBEDDING_DIMS = int(os.getenv("EMBEDDING_DIMS", "384"))
# EMBEDDING_DIMS = int(os.getenv("EMBEDDING_DIMS", "768"))
EMBEDDING_DIMS = int(os.getenv("EMBEDDING_DIMS", "1024"))
QUEUE_MAXSIZE = int(os.getenv("INDEX_QUEUE_MAXSIZE", "2048"))
NLP_SERVICE_URL = os.getenv("NLP_SERVICE_URL", "http://nlp-service:8003")

es_client = None
kafka_consumer = None
consumer_task = None
indexer_task = None
index_queue: asyncio.Queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)

# Client HTTP partagé pour les appels au NLP service
nlp_session: Optional[aiohttp.ClientSession] = None

async def send_terms_to_nlp(terms: list):
    if not terms:
        return
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{NLP_SERVICE_URL}/vocab/update",
                json={"terms": list(set(terms))},
                timeout=5
            )
    except Exception as e:
        logger.warning(f"Erreur envoi vocabulaire NLP: {e}")

async def get_nlp_session() -> aiohttp.ClientSession:
    """Retourne une session aiohttp réutilisable (créée au démarrage)."""
    global nlp_session
    if nlp_session is None or nlp_session.closed:
        nlp_session = aiohttp.ClientSession()
    return nlp_session

NLP_SERVICE_URL = os.getenv("NLP_SERVICE_URL", "http://nlp-service:8003")

async def get_embedding_from_nlp(text: str) -> List[float]:
    global nlp_session
    if nlp_session is None or nlp_session.closed:
        nlp_session = aiohttp.ClientSession()
    try:
        async with nlp_session.post(f"{NLP_SERVICE_URL}/embed", json={"text": text}) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("embedding", [])
            else:
                logger.warning(f"NLP service returned {resp.status}, fallback")
                return embedding_from_text(text, dims=EMBEDDING_DIMS)
    except Exception as e:
        logger.exception(f"Error calling NLP service: {e}")
        return embedding_from_text(text, dims=EMBEDDING_DIMS)

# --- Helper: transform incoming raw doc -> enriched document to index in ES
async def prepare_doc_for_indexing(raw_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Version asynchrone qui appelle le NLP service pour l'embedding.
    Ajoute le nettoyage HTML et la génération du snippet.
    """
    if raw_doc.get('doc_type') == 'image':
        return await prepare_image_for_indexing(raw_doc)

    doc = dict(raw_doc or {})
    # Récupération de l'URL (priorité à response_url puis url)
    url = doc.get("response_url") or doc.get("url")
    if not url:
        logger.warning("Document sans URL ignoré")
        raise ValueError("Document sans URL")
    # Normalisation simple (optionnel)
    url = url.strip()

    # Contenu HTML brut
    content_html = doc.get("extracted_content") or doc.get("content") or extract_text_from_raw_response(doc) or ""

    # Nettoyage HTML -> texte propre + snippet
    cleaned = clean_html(content_html)
    clean_text = cleaned["clean_text"]
    snippet = cleaned["snippet"]

    # Fallback si le nettoyage a échoué 
    if not clean_text and content_html:
        clean_text = re.sub(r'<[^>]+>', ' ', content_html)
        clean_text = ' '.join(clean_text.split())
        snippet = clean_text[:200] + ('...' if len(clean_text) > 200 else '')

    # Nettoyage du titre et de la description (suppression des balises HTML)
    title = doc.get("title") or ""
    title = re.sub(r'<[^>]+>', ' ', title).strip()
    description = doc.get("description") or ""
    description = re.sub(r'<[^>]+>', ' ', description).strip()

    # Embedding sur le texte propre
    embedding_source = clean_text[:4000] if len(clean_text) > 4000 else clean_text
    if not embedding_source.strip():
        embedding_source = "empty document"

    # Embedding (fallback local, sans appeler le NLP service)
    # embedding = embedding_from_text(embedding_source, dims=EMBEDDING_DIMS)
    embedding = await get_embedding_from_nlp(embedding_source)

    # Traitement des médias
    videos_raw = doc.get("videos") or doc.get("video_urls") or []
    videos_processed = process_videos_data(videos_raw) if videos_raw else []
    image_urls = doc.get("image_urls", []) or []
    # Assurer que ce sont des listes
    if isinstance(image_urls, str):
        image_urls = [image_urls]
    if isinstance(videos_processed, str):
        videos_processed = [videos_processed]

    # Enrichissement métadonnées
    enriched = enrich_metadata(doc)

    # Construction du document final
    final = {
        "url": url,
        "title": title,
        "description": description,
        "content": clean_text,                # texte propre pour la recherche
        "snippet": snippet,                   # résumé pour l'affichage
        "extracted_content": doc.get("extracted_content", content_html),
        "image_urls": image_urls,
        "video_urls": [v.get("watch_url") or v.get("video_url") or v.get("embed_url") for v in videos_processed],
        "videos": videos_processed,
        "media_count": doc.get("media_count", 0) or len(image_urls) + len(videos_processed),
        "content_type": doc.get("content_type", "text"),
        "metadata": enriched.get("metadata", {}),
        "keywords_found": doc.get("keywords_found", []),
        "status_code": doc.get("status_code", 200),
        "crawled_at": doc.get("crawled_at") or enriched.get("extracted_at") or datetime.utcnow().isoformat(),
        "timestamp": datetime.utcnow().isoformat(),
        "pagerank": doc.get("pagerank", 0.1),
        "quality_score": doc.get("content_quality", None) or enriched.get("nlp_score", None) or min(1.0, len(clean_text) / 1000.0),
        "embedding": embedding,
        "raw": doc,                         # pour debug, peut être retiré en prod
        "file_type": doc.get('file_type'),
        "file_size": doc.get('file_size'),
        "pages": doc.get('pages'),
        "word_count": doc.get('word_count'),
        "technical_metadata": doc.get("technical_metadata", {}),
        "links": doc.get("links", []),
        "original_file_url": doc.get("metadata", {}).get("minio_url") or doc.get("minio_url"),
    }

    # Titre de secours si vide
    if not final["title"] and doc.get("raw_title"):
        final["title"] = re.sub(r'<[^>]+>', ' ', doc.get("raw_title")).strip()

    # ID déterministe basé sur l'URL
    import hashlib
    doc_id = hashlib.md5(url.encode()).hexdigest()
    final["_id"] = doc_id

    logger.info(f"📄 Document préparé : url={url}, _id={doc_id}, titre={final['title'][:50]}")
    return final

# --- Kafka message parsing (inchangé)
def parse_message_value(raw: Any) -> Dict[str, Any]:
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

# --- Kafka message handler (mettre en file d'attente)
async def handle_kafka_message(msg: ConsumerRecord):
    # Protection : si ES n'est pas connecté, on ignore le message
    if es_client is None:
        logger.warning("ES client not available, skipping message")
        return

    try:
        # Si le message vient du topic YouTube, traitement spécifique
        if msg.topic == "youtube.metadata.updated":
            data = parse_message_value(msg.value)
            doc_id = data.get("doc_id")
            if not doc_id:
                logger.warning("Message YouTube sans doc_id, ignoré")
                return

            if data.get("status") == "unavailable":
                mark_youtube_unavailable(es_client, ES_INDEX, doc_id, data.get("video_id"))
            else:
                update_youtube_metadata(es_client, ES_INDEX, doc_id, data)
            return

        # Traitement normal des documents crawlés
        raw_doc = parse_message_value(msg.value)
        if "payload" in raw_doc and isinstance(raw_doc["payload"], dict):
            raw_doc = raw_doc["payload"]
        final_doc = await prepare_doc_for_indexing(raw_doc)
        doc_id = final_doc.pop("_id", None)
        if doc_id:
            res = es_client.index(index=ES_INDEX, body=final_doc, id=doc_id)
            logger.info(f"✅ Document indexé : {final_doc.get('url')} (id={doc_id})")
        else:
            await index_queue.put(final_doc)

        # Enrichissement du vocabulaire NLP
        doc_terms = (
            raw_doc.get('keywords_found', []) +
            raw_doc.get('technical_metadata', {}).get('programming_languages', []) +
            raw_doc.get('technical_metadata', {}).get('technical_concepts', [])
        )
        if doc_terms:
            await send_terms_to_nlp(doc_terms)

    except Exception as e:
        logger.exception(f"Erreur handle_kafka_message: {e}")


# --- Indexer background task
async def indexer_loop(client, index_name: str):
    buffer: List[Dict[str, Any]] = []
    last_flush = asyncio.get_event_loop().time()

    async def flush_buffer():
        nonlocal buffer, last_flush
        if not buffer:
            return
        try:
            logger.info("Flushing %d docs to ES index=%s", len(buffer), index_name)
            result = index_documents_bulk(client, index_name=index_name, docs=buffer, chunk_size=100, vector_field_name="embedding", vector_dims=EMBEDDING_DIMS, strict=False)
            logger.info(f"Bulk result: {result}")
        except Exception as e:
            logger.exception("Bulk indexing failed: %s", e)
        finally:
            buffer = []
            last_flush = asyncio.get_event_loop().time()

    while True:
        try:
            timeout = max(0.0, BATCH_INTERVAL - (asyncio.get_event_loop().time() - last_flush))
            try:
                doc = await asyncio.wait_for(index_queue.get(), timeout=timeout)
                buffer.append(doc)
                index_queue.task_done()
            except asyncio.TimeoutError:
                pass

            if len(buffer) >= BATCH_SIZE or (buffer and (asyncio.get_event_loop().time() - last_flush) >= BATCH_INTERVAL):
                await flush_buffer()
        except asyncio.CancelledError:
            logger.info("Indexing loop cancelled, flushing remaining %d documents...", len(buffer))
            await flush_buffer()
            raise
        except Exception as e:
            logger.exception("Unexpected error in indexer_loop: %s", e)
            await asyncio.sleep(1)

# --- ES mapping 
ELASTICSEARCH_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "french_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding", "french_elision", "french_stop", "french_stemmer"]
                },
                "code_analyzer": {
                    "type": "custom",
                    "tokenizer": "pattern",
                    "pattern": r"[^\w#@]+|(?<=[a-z])(?=[A-Z])",
                    "filter": ["lowercase"]
                }
            },
            "filter": {
                "french_stop": {"type": "stop", "stopwords": "_french_"},
                "french_stemmer": {"type": "stemmer", "language": "french"},
                "french_elision": {"type": "elision", "articles": ["l", "m", "t", "qu", "n", "s", "j", "d"]}
            }
        }
    },
    "mappings": {
        "dynamic": True,
        "properties": {
            "videos": {
                "type": "nested",
                "properties": {
                    "video_url": {"type": "keyword"},
                    "watch_url": {"type": "keyword"},
                    "embed_url": {"type": "keyword"},
                    "thumbnail": {"type": "keyword"},
                    "platform": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "video_id": {"type": "keyword"}
                }
            },
            "youtube_metadata": {
                "type": "object",
                "properties": {
                    "title": {"type": "text", "analyzer": "french_analyzer"},
                    "description": {"type": "text", "analyzer": "french_analyzer"},
                    "tags": {"type": "keyword"},
                    "view_count": {"type": "integer"},
                    "like_count": {"type": "integer"},
                    "comment_count": {"type": "integer"},
                    "duration_seconds": {"type": "integer"},
                    "thumbnail": {"type": "keyword", "index": False},
                    "default_thumbnail": {"type": "keyword", "index": False},
                    "published_at": {"type": "date"},
                    "channel_title": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "status": {"type": "keyword"}
                }
            },
            "original_file_url": {"type": "keyword"},
            "file_type": {"type": "keyword"},
            "file_size": {"type": "integer"},
            "pages": {"type": "integer"},
            "word_count": {"type": "integer"},
            "keywords_found": {"type": "keyword"},
            "url": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "french_analyzer"},
            "description": {"type": "text", "analyzer": "french_analyzer"},
            "content": {"type": "text", "analyzer": "french_analyzer"},
            "snippet": {"type": "text", "index": False},     
            "extracted_content": {"type": "text", "analyzer": "french_analyzer"},
            "image_urls": {"type": "keyword"},
            "video_urls": {"type": "keyword"},
            "media_count": {"type": "integer"},
            "content_type": {"type": "keyword"},
            "domain": {"type": "keyword"},
            "crawled_at": {"type": "date"},
            "status_code": {"type": "integer"},
            "metadata": {
                "type": "object",
                "dynamic": True
            },
            "timestamp": {"type": "date"},
            "pagerank": {"type": "float"},
            "quality_score": {"type": "float"},
            "embedding": {
                "type": "dense_vector",
                "dims": EMBEDDING_DIMS,
                "index": True,
                "similarity": "cosine"
            },
            "links": {"type": "keyword"}
        }
    }
}

async def prepare_image_for_indexing(raw_doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = dict(raw_doc or {})
    final = {
        "url": doc.get("url"),
        "page_url": doc.get("page_url"),
        "alt": doc.get("alt", ""),
        "img_title": doc.get("img_title", ""),
        "page_title": doc.get("page_title", ""),
        "page_description": doc.get("page_description", ""),
        "content_type": "image",
        "domain": doc.get("domain", ""),
        "crawled_at": doc.get("crawled_at"),
        "timestamp": datetime.utcnow().isoformat(),
        "keywords_found": doc.get("keywords_found", []),
        "metadata": doc.get("metadata", {}),
        "thematic_score": doc.get("thematic_score", 0.0),
    }
    final["_id"] = hashlib.md5(final["url"].encode()).hexdigest()
    logger.info(f"🔍 Image préparée : {final['url']}")
    return final

# --- FastAPI app & lifecycle
app = FastAPI(title="Indexing Service (Integrated)", version="2.0.0")

def needs_recreate(es_client, index_name):
    """Vérifie si l'index a besoin d'être recréé à cause du mauvais type du champ embedding."""
    try:
        mapping = es_client.indices.get_mapping(index=index_name)
        props = mapping.get(index_name, {}).get("mappings", {}).get("properties", {})
        embedding = props.get("embedding", {})
        # Si le champ embedding n'est pas un dense_vector, il faut recréer
        return embedding.get("type") != "dense_vector"
    except Exception:
        # Si l'index n'existe pas, on recrée aussi
        return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    global es_client, kafka_consumer, consumer_task, indexer_task, nlp_session

    loop = asyncio.get_running_loop()

    # create ES client with retry
    for attempt in range(1, 20):
        try:
            es_client = get_es_client_with_retry(
                hosts=getattr(settings, "ES_HOSTS", None),
                user=getattr(settings, "ES_USER", None),
                password=getattr(settings, "ES_PASSWORD", None),
                max_retries=3,
                retry_delay=5,
            )
            if es_client.ping():
                logger.info(f"Connected to Elasticsearch (attempt {attempt})")
                break
        except Exception:
            logger.warning(f"ES not ready, attempt {attempt}/20, retrying in 5s...")
            time.sleep(5)
    else:
        logger.error("Could not connect to ES after 20 attempts")
        es_client = None

    # create index if not exists
    if es_client:
        try:
            if not es_client.indices.exists(index=ES_INDEX):
                es_client.indices.create(index=ES_INDEX, body=ELASTICSEARCH_MAPPING)
                logger.info("Created ES index %s", ES_INDEX)
            else:
                if needs_recreate(es_client, ES_INDEX):
                    logger.warning("Index %s has incorrect mapping for embedding, deleting and recreating...", ES_INDEX)
                    es_client.indices.delete(index=ES_INDEX)
                    es_client.indices.create(index=ES_INDEX, body=ELASTICSEARCH_MAPPING)
                    logger.info("Recreated ES index %s with correct mapping", ES_INDEX)
                else:
                    logger.info("ES index %s already exists and mapping is correct", ES_INDEX)
        except Exception as e:
            logger.exception("Failed to ensure ES index: %s", e)

    # create shared aiohttp session
    nlp_session = aiohttp.ClientSession()
    logger.info("Created shared aiohttp session for NLP service")

    # start Kafka consumer
    disable_kafka = os.getenv("DISABLE_KAFKA", "false").lower() == "true"
    if not disable_kafka:
        try:
            kafka_conf = {
                "bootstrap.servers": getattr(settings, "KAFKA_BROKERS"),
                "group.id": getattr(settings, "KAFKA_GROUP_ID", "indexer-group"),
                "auto.offset.reset": "earliest",
            }
            kafka_topics = [
                getattr(settings, "KAFKA_TOPIC", "crawled_documents"),
                "youtube.metadata.updated"   # nouveau topic
            ]
            kafka_consumer = AIOConsumer(kafka_conf, kafka_topics, loop)
            consumer_task = loop.create_task(kafka_consumer.consume(handle_kafka_message))
            logger.info("Kafka consumer started on topics %s", kafka_topics)
        except Exception as e:
            logger.exception("Failed to start Kafka consumer: %s", e)
            kafka_consumer = None

    # start indexer loop if es_client available
    if es_client:
        indexer_task = loop.create_task(indexer_loop(es_client, ES_INDEX))
        logger.info("Indexer background task started (batch_size=%s interval=%s)", BATCH_SIZE, BATCH_INTERVAL)
    else:
        logger.warning("ES client not available: indexer not started")

    yield

    # graceful shutdown: cancel tasks and close session
    logger.info("Shutting down: cancelling background tasks...")
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Kafka consumer task cancelled")
    if indexer_task:
        indexer_task.cancel()
        try:
            await indexer_task
        except asyncio.CancelledError:
            logger.info("Indexer task cancelled")
    if nlp_session and not nlp_session.closed:
        await nlp_session.close()
        logger.info("Closed aiohttp session")

app.router.lifespan_context = lifespan

# --- HTTP endpoints
@app.get("/health")
async def health():
    status = {"service": "indexing", "timestamp": datetime.utcnow().isoformat()}
    if es_client:
        try:
            if es_client.ping():
                status["elasticsearch"] = "ok"
            else:
                status["elasticsearch"] = "ping_failed"
        except Exception as e:
            status["elasticsearch"] = f"error: {e}"
    else:
        status["elasticsearch"] = "not_connected"
    return status

@app.get("/")
async def root():
    return {"message": "Indexing Service OK", "index": ES_INDEX}

@app.post("/index-manual")
async def index_manual(doc: Dict[str, Any]):
    if es_client is None:
        return {"status": "error", "message": "ES not connected"}
    prepared = await prepare_doc_for_indexing(doc)
    try:
        res = es_client.index(index=ES_INDEX, body=prepared)
        return {"status": "ok", "_id": res.get("_id")}
    except Exception as e:
        logger.exception("Manual index failed: %s", e)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("SERVICE_PORT", 8001)), log_level="info")