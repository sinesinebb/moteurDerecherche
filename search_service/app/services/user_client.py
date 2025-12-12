# services/user_client.py
import httpx
from typing import Optional, Dict
from models.schemas import UserProfile, SearchPreferences

class UserServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10.0)
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Récupère le profil utilisateur pour la personnalisation"""
        try:
            response = await self.client.get(f"/api/users/{user_id}/profile")
            if response.status_code == 200:
                return UserProfile(**response.json())
        except Exception as e:
            print(f"Error fetching user profile: {e}")
        return None
    
    async def get_search_preferences(self, user_id: str) -> SearchPreferences:
        """Récupère les préférences de recherche de l'utilisateur"""
        try:
            response = await self.client.get(f"/api/users/{user_id}/search-preferences")
            if response.status_code == 200:
                return SearchPreferences(**response.json())
        except Exception:
            pass
        return SearchPreferences()  # Retourne les préférences par défaut
    
    async def save_search_history(self, user_id: str, query: str, results_count: int):
        """Sauvegarde l'historique de recherche (asynchrone)"""
        try:
            await self.client.post(f"/api/users/{user_id}/search-history", json={
                "query": query,
                "results_count": results_count,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f"Error saving search history: {e}")
    
    async def validate_token(self, token: str) -> Optional[Dict]:
        """Valide le token JWT avec le User Service"""
        try:
            response = await self.client.post("/api/auth/validate-token", json={"token": token})
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Token validation error: {e}")
        return None