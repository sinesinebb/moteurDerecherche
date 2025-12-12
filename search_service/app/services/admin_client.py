# services/admin_client.py
import httpx
from typing import Dict

class AdminServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=5.0)
    
    async def report_search_metrics(self, metrics: Dict):
        """Rapporte les métriques de recherche pour le monitoring admin"""
        try:
            await self.client.post("/api/admin/search-metrics", json=metrics)
        except Exception as e:
            print(f"Error reporting search metrics: {e}")
    
    async def get_system_health(self) -> Dict:
        """Récupère l'état de santé du système pour les checks"""
        try:
            response = await self.client.get("/api/admin/system-health")
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {"status": "unknown", "last_check": None}