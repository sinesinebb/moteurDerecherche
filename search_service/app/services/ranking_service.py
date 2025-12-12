# services/ranking_service.py
from typing import List, Dict
from datetime import datetime
import math
from models.schemas import SearchResult

class RankingService:
    def __init__(self):
        self.weights = {
            'relevance': 0.4,      # Score de pertinence Elasticsearch
            'page_rank': 0.3,      # Autorité de la page
            'freshness': 0.15,     # Fraîcheur du contenu
            'domain_authority': 0.1, # Autorité du domaine
            'content_quality': 0.05 # Qualité du contenu
        }
    
    def rank_results(self, results: List[SearchResult], query: str = None) -> List[SearchResult]:
        """Applique l'algorithme de ranking aux résultats"""
        
        scored_results = []
        for result in results:
            score = self._calculate_composite_score(result, query)
            scored_results.append((result, score))
        
        # Trier par score décroissant
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Mettre à jour les scores de pertinence
        ranked_results = []
        for i, (result, score) in enumerate(scored_results):
            result.relevance_score = score
            result.rank = i + 1
            ranked_results.append(result)
        
        return ranked_results
    
    def _calculate_composite_score(self, result: SearchResult, query: str = None) -> float:
        """Calcule un score composite pour un résultat"""
        
        # Score de base Elasticsearch (normalisé)
        relevance_score = self._normalize_score(result.relevance_score, 0, 50)
        
        # Score PageRank
        page_rank_score = min(result.page_rank / 10, 1.0)
        
        # Score de fraîcheur
        freshness_score = self._calculate_freshness_score(result.published_date)
        
        # Score d'autorité du domaine
        domain_score = self._calculate_domain_score(result.domain)
        
        # Score de qualité du contenu
        content_score = self._calculate_content_quality_score(result)
        
        # Combinaison pondérée
        composite_score = (
            self.weights['relevance'] * relevance_score +
            self.weights['page_rank'] * page_rank_score +
            self.weights['freshness'] * freshness_score +
            self.weights['domain_authority'] * domain_score +
            self.weights['content_quality'] * content_score
        )
        
        return composite_score
    
    def _normalize_score(self, score: float, min_val: float, max_val: float) -> float:
        """Normalise un score entre 0 et 1"""
        if score <= min_val:
            return 0.0
        elif score >= max_val:
            return 1.0
        else:
            return (score - min_val) / (max_val - min_val)
    
    def _calculate_freshness_score(self, published_date: datetime) -> float:
        """Calcule le score de fraîcheur"""
        if not published_date:
            return 0.5
        
        now = datetime.now()
        days_old = (now - published_date).days
        
        if days_old < 7:    # Moins d'une semaine
            return 1.0
        elif days_old < 30: # Moins d'un mois
            return 0.8
        elif days_old < 90: # Moins de 3 mois
            return 0.6
        elif days_old < 365: # Moins d'un an
            return 0.4
        else:               # Plus d'un an
            return 0.2
    
    def _calculate_domain_score(self, domain: str) -> float:
        """Calcule le score d'autorité du domaine"""
        authority_domains = {
            'github.com': 0.9,
            'stackoverflow.com': 0.9,
            'docs.python.org': 0.8,
            'developer.mozilla.org': 0.8,
            'microsoft.com': 0.7,
            'oracle.com': 0.7,
            'python.org': 0.8,
            'docker.com': 0.7,
            'kubernetes.io': 0.7
        }
        
        return authority_domains.get(domain, 0.5)
    
    def _calculate_content_quality_score(self, result: SearchResult) -> float:
        """Estime la qualité du contenu"""
        score = 0.5  # Score de base
        
        # Bonus pour la présence de description
        if result.description and len(result.description) > 50:
            score += 0.2
        
        # Bonus pour la longueur du snippet
        if result.content_snippet and len(result.content_snippet) > 100:
            score += 0.2
        
        # Bonus pour les highlights
        if result.highlights and len(result.highlights) > 0:
            score += 0.1
        
        return min(score, 1.0)