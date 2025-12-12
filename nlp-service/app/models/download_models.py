# nlp-service/app/download_models.py
#!/usr/bin/env python3
"""
Script pour télécharger les modèles NLP au démarrage
"""
import spacy
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_models():
    """Télécharge tous les modèles NLP nécessaires"""
    logger.info("📥 Téléchargement des modèles NLP...")
    
    try:
        # Télécharger le modèle spaCy français
        logger.info("📥 Téléchargement de fr_core_news_sm...")
        spacy.cli.download("fr_core_news_sm")
        logger.info("✅ fr_core_news_sm téléchargé")
        
        # Charger le modèle pour vérification
        nlp = spacy.load("fr_core_news_sm")
        logger.info("✅ Modèle spaCy chargé avec succès")
        
        # Télécharger le modèle sentence-transformers
        logger.info("📥 Téléchargement de paraphrase-multilingual-MiniLM-L12-v2...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("✅ Modèle sentence-transformers chargé avec succès")
        
        # Test du modèle
        test_embedding = model.encode(["test de fonctionnement"])
        logger.info(f"✅ Embedding test généré: dimension {test_embedding.shape}")
        
        logger.info("🎉 Tous les modèles NLP sont prêts!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du téléchargement des modèles: {e}")
        raise

if __name__ == "__main__":
    download_models()