# nlp-service/app/nlp_processor_simple.py
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class SimpleNLPProcessor:
    def __init__(self):
        logger.info("🚀 Initialisation du SimpleNLPProcessor...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("✅ SimpleNLPProcessor prêt!")

    def expand_query(self, query: str) -> dict:
        embedding = self.model.encode(query).tolist()
        return {
            "original_query": query,
            "enhanced_query": {"text": query},
            "entities": {},
            "intent": "general",
            "expanded_terms": [],
            "semantic_embedding": embedding
        }