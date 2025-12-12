# search_service/app/hybrid_search.py
from typing import List, Dict, Any
import numpy as np

class HybridSearch:
    def __init__(self, semantic_search):
        self.semantic_search = semantic_search
        
    def hybrid_search(self, query: str, lexical_results: List[Dict], alpha: float = 0.7) -> List[Dict]:
        """
        Combine recherche lexicale et sémantique
        alpha: poids de la recherche sémantique (0.7 = 70% sémantique, 30% lexical)
        """
        # Recherche sémantique
        semantic_results = self.semantic_search.semantic_search(query, k=50)
        
        # Fusion des résultats
        all_docs = {}
        
        # Ajouter les résultats lexicaux
        for doc in lexical_results:
            doc_id = doc.get('id')
            all_docs[doc_id] = {
                'doc': doc,
                'lexical_score': doc.get('score', 0),
                'semantic_score': 0
            }
        
        # Ajouter/mettre à jour avec les résultats sémantiques
        for doc in semantic_results:
            doc_id = doc.get('id')
            if doc_id in all_docs:
                all_docs[doc_id]['semantic_score'] = doc.get('semantic_score', 0)
            else:
                all_docs[doc_id] = {
                    'doc': doc,
                    'lexical_score': 0,
                    'semantic_score': doc.get('semantic_score', 0)
                }
        
        # Calcul du score hybride
        hybrid_results = []
        for doc_id, scores in all_docs.items():
            lexical_norm = self._normalize_score(scores['lexical_score'], 0, 100)  # Normaliser entre 0-1
            semantic_norm = scores['semantic_score']  # Déjà entre 0-1
            
            hybrid_score = (alpha * semantic_norm) + ((1 - alpha) * lexical_norm)
            
            result = scores['doc'].copy()
            result['hybrid_score'] = hybrid_score
            result['lexical_score'] = scores['lexical_score']
            result['semantic_score'] = scores['semantic_score']
            hybrid_results.append(result)
        
        # Trier par score hybride
        hybrid_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        return hybrid_results[:20]
    
    def _normalize_score(self, score, min_val, max_val):
        """Normalise un score entre 0 et 1"""
        if max_val - min_val == 0:
            return 0
        return (score - min_val) / (max_val - min_val)