# services/indexing_client.py
import httpx
from typing import List, Dict

class IndexingServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=5.0)
    
    async def get_document_metadata(self, doc_ids: List[str]) -> Dict[str, Dict]:
        """Récupère les métadonnées des documents"""
        try:
            response = await self.client.post("/api/indexing/documents/metadata", json={"doc_ids": doc_ids})
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching document metadata: {e}")
        return {}
    
    async def get_index_stats(self) -> Dict:
        """Récupère les statistiques de l'index"""
        try:
            response = await self.client.get("/api/indexing/stats")
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {"total_documents": 0, "last_update": None}
    
    async def trigger_reindexing(self, doc_ids: List[str] = None):
        """Déclenche une réindexation (pour l'admin)"""
        try:
            payload = {"doc_ids": doc_ids} if doc_ids else {}
            await self.client.post("/api/indexing/reindex", json=payload)
        except Exception as e:
            print(f"Error triggering reindexing: {e}")