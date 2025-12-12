# services/pagerank_client.py
import httpx
from typing import List, Dict

class PageRankClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=15.0)
    
    async def get_realtime_scores(self, doc_ids: List[str]) -> Dict[str, float]:
        """Récupère les scores PageRank en temps réel"""
        try:
            response = await self.client.post("/api/pagerank/scores/batch", json={"doc_ids": doc_ids})
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching PageRank scores: {e}")
        return {}
    
    async def calculate_query_specific_rank(self, query: str, doc_ids: List[str]) -> Dict[str, float]:
        """Calcule un ranking spécifique à la requête"""
        try:
            response = await self.client.post("/api/pagerank/query-specific", json={
                "query": query,
                "doc_ids": doc_ids
            })
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {}