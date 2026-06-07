import logging
import threading
import time
from fastapi import FastAPI
from src.core.config import settings
from src.api.routes import router

logger = logging.getLogger(__name__)

def scheduled_pagerank():
    """Fonction périodique pour recalculer le PageRank (ex: toutes les heures)."""
    while True:
        try:
            logger.info("Déclenchement du calcul PageRank planifié...")
            # Appeler la fonction de calcul ici (via routes ou directement)
            # Exemple: from src.api.routes import compute_all; compute_all()
            time.sleep(3600)  # 1 heure
        except Exception as e:
            logger.exception("Erreur lors du calcul planifié")
            time.sleep(60)

# Lancer le thread au démarrage (optionnel)
thread = threading.Thread(target=scheduled_pagerank, daemon=True)
thread.start()

app = FastAPI(
    title="PageRank Service", 
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "pagerank",
        "version": "1.0.0"
    }

# Alternative avec slash pour compatibilité
@app.get("/health/")
async def health_check_slash():
    return {
        "status": "healthy", 
        "service": "pagerank",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "PageRank Service is running",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.service_port)