# services/cache_service.py
import redis.asyncio as redis
import json
import pickle
from typing import Optional, Any, List
import hashlib
from core.config import settings

class SearchCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = settings.cache_ttl
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Génère une clé de cache unique"""
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupère un objet du cache"""
        try:
            data = await self.redis.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Stocke un objet dans le cache"""
        try:
            serialized = pickle.dumps(value)
            actual_ttl = ttl or self.default_ttl
            await self.redis.setex(key, actual_ttl, serialized)
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
    
    async def delete(self, key: str):
        """Supprime une clé du cache"""
        try:
            await self.redis.delete(key)
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
    
    async def clear_pattern(self, pattern: str):
        """Supprime toutes les clés correspondant au motif"""
        try:
            keys = await self.redis.keys(f"{pattern}*")
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
    
    async def get_search_cache(self, search_request: dict) -> Optional[Any]:
        """Récupère les résultats de recherche du cache"""
        cache_key = self._generate_key("search", search_request)
        return await self.get(cache_key)
    
    async def set_search_cache(self, search_request: dict, results: Any, ttl: int = None):
        """Stocke les résultats de recherche dans le cache"""
        cache_key = self._generate_key("search", search_request)
        await self.set(cache_key, results, ttl)
    
    async def get_autocomplete_cache(self, prefix: str) -> Optional[List[str]]:
        """Récupère les suggestions d'autocomplétion du cache"""
        cache_key = f"autocomplete:{prefix}"
        return await self.get(cache_key)
    
    async def set_autocomplete_cache(self, prefix: str, suggestions: List[str]):
        """Stocke les suggestions d'autocomplétion dans le cache"""
        cache_key = f"autocomplete:{prefix}"
        await self.set(cache_key, suggestions, ttl=3600)  # 1 heure
    
    async def increment_search_counter(self, query: str):
        """Incrémente le compteur de recherche pour les tendances"""
        try:
            await self.redis.zincrby("search_trends", 1, query.lower())
        except Exception as e:
            print(f"Error incrementing search counter: {e}")
    
    async def get_popular_searches(self, limit: int = 10) -> List[tuple]:
        """Récupère les recherches populaires"""
        try:
            results = await self.redis.zrevrange("search_trends", 0, limit-1, withscores=True)
            return [(search.decode() if isinstance(search, bytes) else search, score) 
                   for search, score in results]
        except Exception as e:
            print(f"Error getting popular searches: {e}")
            return []