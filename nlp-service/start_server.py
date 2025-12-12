# nlp-service/start_server.py
#!/usr/bin/env python3
"""
Script de démarrage optimisé pour le NLP Service
"""
import time
import logging
import uvicorn
import sys
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Point d'entrée principal"""
    logger.info("🚀 Démarrage du NLP Service...")
    
    # Les modèles sont déjà téléchargés depuis le Dockerfile
    # On peut directement démarrer le serveur
    logger.info("✅ Modèles NLP prêts")
    logger.info("🎉 Démarrage du serveur FastAPI...")
    
    # Démarrer le serveur
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8003,
        log_level="info",
        reload=False  # Désactiver le reload en production
    )

if __name__ == "__main__":
    main()