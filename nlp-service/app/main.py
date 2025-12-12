from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import threading
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NLP Service",
    description="Service de traitement du langage naturel pour le moteur de recherche",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
nlp_processor = None
models_loading = False
models_loaded = False
load_error = None
startup_time = time.time()

class QueryRequest(BaseModel):
    query: str
    expand: bool = True
    detect_intent: bool = True

class QueryResponse(BaseModel):
    original_query: str
    enhanced_query: Dict[str, Any]
    entities: Dict[str, List[str]]
    intent: str
    expanded_terms: List[str]
    semantic_embedding: List[float]

class HealthResponse(BaseModel):
    status: str
    service: str
    models_loaded: bool
    models_loading: bool
    version: str
    load_error: Optional[str] = None
    startup_time: float
    current_time: float

def load_models_safe():
    """Charge les modèles NLP de manière sécurisée"""
    global nlp_processor, models_loading, models_loaded, load_error
    
    models_loading = True
    load_error = None
    
    try:
        logger.info("Tentative de chargement des modèles NLP...")
        
        # Essayer d'abord le processeur simple
        try:
            from app.nlp_processor_simple import SimpleNLPProcessor
            nlp_processor = SimpleNLPProcessor()
            models_loaded = True
            models_loading = False
            logger.info("SimpleNLPProcessor chargé avec succès")
            return
        except Exception as e:
            logger.warning(f"SimpleNLPProcessor échoué: {e}")
        
        # Ensuite essayer le processeur complet
        try:
            from app.nlp_processor import NLPProcessor
            nlp_processor = NLPProcessor()
            models_loaded = True
            models_loading = False
            logger.info("NLPProcessor complet chargé avec succès")
            return
        except Exception as e:
            logger.error(f"NLPProcessor complet échoué: {e}")
            raise
        
    except Exception as e:
        models_loading = False
        models_loaded = False
        load_error = str(e)
        logger.error(f"Echec du chargement des modèles: {e}")

def load_models_async():
    """Charge les modèles en arrière-plan"""
    thread = threading.Thread(target=load_models_safe)
    thread.daemon = True
    thread.start()

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    logger.info("Démarrage du NLP Service...")
    logger.info("Les modèles NLP se chargeront en arrière-plan...")
    load_models_async()

@app.post("/enhance-query", response_model=QueryResponse)
async def enhance_query(request: QueryRequest):
    """Améliore une requête de recherche avec NLP"""
    global nlp_processor, models_loading, models_loaded
    
    if models_loading:
        raise HTTPException(
            status_code=503, 
            detail="Les modèles NLP sont en cours de chargement. Veuillez réessayer dans quelques minutes."
        )
    
    if not models_loaded or nlp_processor is None:
        raise HTTPException(
            status_code=503,
            detail="Les modèles NLP ne sont pas encore disponibles. Le service est en cours d'initialisation."
        )
    
    try:
        logger.info(f"Traitement de la requête: '{request.query}'")
        result = nlp_processor.expand_query(request.query)
        
        logger.info(f"Requête améliorée: {len(result['expanded_terms'])} termes, intent: {result['intent']}")
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Erreur traitement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de traitement: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de santé"""
    global nlp_processor, models_loaded, models_loading, load_error, startup_time
    
    status = "healthy" if models_loaded else "unhealthy"
    if models_loading:
        status = "initializing"
    
    return HealthResponse(
        status=status,
        service="nlp",
        models_loaded=models_loaded,
        models_loading=models_loading,
        version="1.0.0",
        load_error=load_error,
        startup_time=startup_time,
        current_time=time.time()
    )

@app.get("/")
async def root():
    """Page d'accueil"""
    global models_loaded, models_loading
    
    status = "operational" if models_loaded else "initializing"
    if models_loading:
        status = "loading_models"
    
    return {
        "message": "NLP Service du Moteur de Recherche Informatique",
        "version": "1.0.0",
        "status": status,
        "models_ready": models_loaded,
        "endpoints": {
            "health": "/health",
            "enhance_query": "/enhance-query (POST)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
