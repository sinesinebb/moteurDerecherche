# search_service/app/semantic_search.py
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SemanticSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Modèle léger et efficace
        self.index = None
        self.documents = []
        
    def build_index(self, documents: List[Dict[str, Any]]):
        """Construit l'index sémantique FAISS"""
        if not documents:
            return
            
        texts = [doc.get('content', '') + " " + doc.get('title', '') for doc in documents]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # Création de l'index FAISS
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Similarité cosinus
        self.index.add(embeddings.astype('float32'))
        self.documents = documents
        
        logger.info(f"✅ Index sémantique construit avec {len(documents)} documents")
    
    def semantic_search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Recherche sémantique"""
        if self.index is None:
            return []
            
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['semantic_score'] = float(score)
                results.append(doc)
                
        return results