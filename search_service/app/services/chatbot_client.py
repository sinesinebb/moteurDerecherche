# services/chatbot_client.py
import httpx
from typing import Dict, List

class ChatbotServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10.0)
    
    async def get_contextual_search(self, query: str, conversation_history: List[Dict]) -> Dict:
        """Obtient une recherche contextualisée pour le chatbot"""
        try:
            response = await self.client.post("/api/chatbot/contextual-search", json={
                "query": query,
                "conversation_history": conversation_history
            })
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error with contextual search: {e}")
        return {"query": query, "filters": {}}
    
    async def log_chatbot_interaction(self, user_id: str, query: str, results_used: List[str]):
        """Log les interactions du chatbot pour l'apprentissage"""
        try:
            await self.client.post("/api/chatbot/interactions/log", json={
                "user_id": user_id,
                "query": query,
                "results_used": results_used,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f"Error logging chatbot interaction: {e}")