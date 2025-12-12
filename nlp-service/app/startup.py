# nlp-service/app/startup.py
#!/usr/bin/env python3
import time
import spacy
from sentence_transformers import SentenceTransformer
import uvicorn
import logging
import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_models():
    """Télécharge les modèles NLP"""
    logger.info("🚀 Démarrage du NLP Service...")
    logger.info("📥 Téléchargement des modèles NLP (cela peut prendre plusieurs minutes)...")
    
    # Télécharger le modèle spaCy
    try:
        logger.info("📥 Téléchargement de fr_core_news_sm...")
        spacy.cli.download('fr_core_news_sm')
        logger.info("✅ fr_core_news_sm téléchargé")
    except Exception as e:
        logger.error(f"⚠️ Erreur spaCy: {e}")
    
    # Charger le modèle SentenceTransformer
    try:
        logger.info("📥 Chargement de SentenceTransformer...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("✅ SentenceTransformer chargé")
    except Exception as e:
        logger.error(f"⚠️ Erreur SentenceTransformer: {e}")
    
    logger.info("🎉 Démarrage du serveur...")

if __name__ == "__main__":
    download_models()
    
    # Import après le téléchargement des modèles
    from app.main import app
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")