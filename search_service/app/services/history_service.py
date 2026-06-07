# search-service/app/services/history_service.py
from datetime import datetime
from typing import List, Dict, Any
import json

class SearchHistoryService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.history_key_prefix = "search_history:"
    
    async def save_search(self, user_id: str, query: str, results_count: int, filters: Dict = None):
        """Sauvegarder une recherche dans l'historique dans le compte de chaque utilisateur"""
        search_entry = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results_count": results_count,
            "filters": filters or {},
            "user_id": user_id
        }
        
        key = f"{self.history_key_prefix}{user_id}"
        await self.redis.lpush(key, json.dumps(search_entry))
        await self.redis.ltrim(key, 0, 99)  # Garder les 100 dernières
        
        return search_entry
    
    async def get_user_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Récupérer l'historique d'un utilisateur"""
        key = f"{self.history_key_prefix}{user_id}"
        history_data = await self.redis.lrange(key, 0, limit - 1)
        
        return [json.loads(entry) for entry in history_data]
    
    async def export_history(self, user_id: str, format: str = "json") -> str:
        """Exporter l'historique dans différents formats"""
        history = await self.get_user_history(user_id, limit=1000)
        
        if format == "json":
            return json.dumps(history, indent=2, ensure_ascii=False)
        elif format == "csv":
            csv_lines = ["query,timestamp,results_count"]
            for entry in history:
                csv_lines.append(
                    f'"{entry["query"]}",{entry["timestamp"]},{entry["results_count"]}'
                )
            return "\n".join(csv_lines)
 
