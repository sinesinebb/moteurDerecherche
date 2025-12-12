# search_service/app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import time
import requests
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Search Service API",
    description="Microservice de recherche spécialisé en informatique",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ELASTICSEARCH_URL = "http://elasticsearch:9200"
INDEX_NAME = "tech_docs"

# Modèles Pydantic
class SearchRequest(BaseModel):
    query: str
    size: int = 10
    page: int = 1
    content_type: Optional[str] = "all"  # "all", "images", "videos", "web"

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    query: str
    processing_time: float
    page: int
    total_pages: int
    content_type: str

class HealthResponse(BaseModel):
    status: str
    elasticsearch: str
    index_exists: bool
    document_count: int
    timestamp: str

def check_elasticsearch_connection() -> bool:
    """Vérifie la connexion à Elasticsearch"""
    try:
        response = requests.get(f"{ELASTICSEARCH_URL}/_cluster/health", timeout=10)
        logger.info(f"Elasticsearch health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erreur de connexion Elasticsearch: {e}")
        return False

def build_search_query(query: str, content_type: str = "all"):
    """Construit la requête Elasticsearch en fonction du type de contenu"""
    
    base_query = {
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "content^2", "description^1.5", "tags^2"],
                        "fuzziness": "AUTO"
                    }
                }
            }
        }
    }
    
    # Filtres par type de contenu
    if content_type == "images":
        base_query["query"]["bool"]["filter"] = {
            "bool": {
                "should": [
                    {"wildcard": {"url": "*.jpg"}},
                    {"wildcard": {"url": "*.jpeg"}},
                    {"wildcard": {"url": "*.png"}},
                    {"wildcard": {"url": "*.gif"}},
                    {"wildcard": {"url": "*.webp"}},
                    {"exists": {"field": "image_url"}}
                ]
            }
        }
    elif content_type == "videos":
        base_query["query"]["bool"]["filter"] = {
            "bool": {
                "should": [
                    {"wildcard": {"url": "*youtube.com*"}},
                    {"wildcard": {"url": "*youtu.be*"}},
                    {"wildcard": {"url": "*vimeo.com*"}},
                    {"wildcard": {"url": "*.mp4"}},
                    {"wildcard": {"url": "*.avi"}},
                    {"wildcard": {"url": "*.mov"}},
                    {"exists": {"field": "video_url"}}
                ]
            }
        }
    elif content_type == "web":
        base_query["query"]["bool"]["must_not"] = {
            "bool": {
                "should": [
                    {"wildcard": {"url": "*.jpg"}},
                    {"wildcard": {"url": "*.jpeg"}},
                    {"wildcard": {"url": "*.png"}},
                    {"wildcard": {"url": "*.gif"}},
                    {"wildcard": {"url": "*youtube.com*"}},
                    {"wildcard": {"url": "*.mp4"}}
                ]
            }
        }
    
    return base_query

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de santé simplifié"""
    try:
        es_ok = check_elasticsearch_connection()
        index_exists = False
        doc_count = 0
        
        if es_ok:
            # Vérifier si l'index existe
            try:
                index_response = requests.get(f"{ELASTICSEARCH_URL}/_cat/indices/{INDEX_NAME}?format=json", timeout=5)
                index_exists = index_response.status_code == 200 and len(index_response.json()) > 0
                
                if index_exists:
                    # Compter les documents
                    count_response = requests.get(f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_count", timeout=5)
                    if count_response.status_code == 200:
                        doc_count = count_response.json().get('count', 0)
            except Exception as e:
                logger.warning(f"Erreur vérification index: {e}")
        
        return HealthResponse(
            status="healthy" if es_ok else "unhealthy",
            elasticsearch="connected" if es_ok else "disconnected",
            index_exists=index_exists,
            document_count=doc_count,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="error",
            elasticsearch="error",
            index_exists=False,
            document_count=0,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

@app.post("/search", response_model=SearchResponse)
async def search_post(request: SearchRequest):
    """Endpoint de recherche POST avec support des types de contenu"""
    start_time = time.time()
    
    # Validation de la requête
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="La requête de recherche est requise")
    
    # Vérification de la connexion Elasticsearch
    if not check_elasticsearch_connection():
        raise HTTPException(status_code=503, detail="Service Elasticsearch indisponible")
    
    try:
        logger.info(f"🔍 Recherche: '{request.query}' - Type: {request.content_type}")
        
        # Construire la requête avec filtres
        search_body = build_search_query(request.query, request.content_type)
        search_body["from"] = (request.page - 1) * request.size
        search_body["size"] = request.size
        
        # Ajouter le highlight pour les snippets
        search_body["highlight"] = {
            "fields": {
                "content": {"fragment_size": 150, "number_of_fragments": 1},
                "title": {"fragment_size": 100, "number_of_fragments": 1}
            }
        }
        
        response = requests.post(
            f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search",
            json=search_body,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Elasticsearch error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="Erreur lors de la recherche")
        
        data = response.json()
        hits = data.get('hits', {}).get('hits', [])
        total = data.get('hits', {}).get('total', {}).get('value', 0)
        
        # Traitement des résultats
        results = []
        for hit in hits:
            source = hit.get('_source', {})
            highlight = hit.get('highlight', {})
            
            # Déterminer le type de contenu
            content_type = "web"
            url = source.get('url', '')
            
            # Détection automatique du type
            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                content_type = "image"
            elif any(domain in url for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
                content_type = "video"
            elif any(ext in url.lower() for ext in ['.mp4', '.avi', '.mov', '.webm']):
                content_type = "video"
            
            # Construire le snippet
            snippet = ""
            if highlight.get('content'):
                snippet = highlight['content'][0]
            elif highlight.get('title'):
                snippet = highlight['title'][0]
            else:
                content = source.get('content', '')
                snippet = content[:150] + "..." if len(content) > 150 else content
            
            # Extraire l'URL de l'image/vidéo si disponible
            media_url = source.get('image_url') or source.get('video_url') or url
            
            result = {
                "id": hit.get('_id'),
                "title": source.get('title', 'Sans titre'),
                "url": url,
                "media_url": media_url,  # URL spécifique pour le média
                "domain": source.get('domain', 'unknown'),
                "snippet": snippet,
                "score": round(hit.get('_score', 0), 3),
                "content_type": content_type,
                "thumbnail": source.get('thumbnail'),  # Pour les previews
                "duration": source.get('duration'),  # Pour les vidéos
                "file_size": source.get('file_size'),  # Pour les images
            }
            results.append(result)
        
        processing_time = time.time() - start_time
        total_pages = (total + request.size - 1) // request.size if total > 0 else 0
        
        logger.info(f"✅ Recherche terminée: {len(results)} résultats en {processing_time:.3f}s")
        
        return SearchResponse(
            results=results,
            total=total,
            query=request.query,
            processing_time=round(processing_time, 3),
            page=request.page,
            total_pages=total_pages,
            content_type=request.content_type
        )
        
    except requests.exceptions.Timeout:
        logger.error("⏰ Timeout lors de la recherche Elasticsearch")
        raise HTTPException(status_code=504, detail="Timeout de la recherche")
    except Exception as e:
        logger.error(f"❌ Erreur recherche: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/search")
async def search_get(
    q: str = Query(..., description="Requête de recherche"),
    size: int = Query(10, ge=1, le=100, description="Nombre de résultats"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    content_type: str = Query("all", description="Type de contenu: all, images, videos, web")
):
    """Endpoint de recherche GET avec filtres"""
    return await search_post(SearchRequest(query=q, size=size, page=page, content_type=content_type))

# Nouveaux endpoints spécifiques
@app.get("/search/images")
async def search_images(
    q: str = Query(..., description="Requête de recherche"),
    size: int = Query(20, ge=1, le=50, description="Nombre de résultats"),
    page: int = Query(1, ge=1, description="Numéro de page")
):
    """Recherche spécifique aux images"""
    return await search_post(SearchRequest(query=q, size=size, page=page, content_type="images"))

@app.get("/search/videos")
async def search_videos(
    q: str = Query(..., description="Requête de recherche"),
    size: int = Query(20, ge=1, le=50, description="Nombre de résultats"),
    page: int = Query(1, ge=1, description="Numéro de page")
):
    """Recherche spécifique aux vidéos"""
    return await search_post(SearchRequest(query=q, size=size, page=page, content_type="videos"))

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    health = await health_check()
    return {
        "message": "🔍 Search Service - Moteur de Recherche Informatique",
        "status": health.status,
        "version": "2.0.0",
        "elasticsearch": health.elasticsearch,
        "document_count": health.document_count,
        "endpoints": {
            "search": "/search",
            "images": "/search/images",
            "videos": "/search/videos",
            "health": "/health"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Log au démarrage"""
    logger.info("🚀 Starting Search Service...")
    health = await health_check()
    logger.info(f"📊 Health status: {health.status}, ES: {health.elasticsearch}, Docs: {health.document_count}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)