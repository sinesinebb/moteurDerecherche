# database/redis.py
import redis.asyncio as redis
from app.core.config import settings  # CORRECTION: ajouter app.
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.client = None
    
    async def connect(self):
        """Établit la connexion à Redis"""
        try:
            # CORRECTION: utiliser les paramètres de settings
            redis_host = getattr(settings, 'REDIS_HOST', 'redis')
            redis_port = getattr(settings, 'REDIS_PORT', 6379)
            
            self.client = redis.Redis(
                host=redis_host,
                port=redis_port,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                retry_on_timeout=True
            )
            # Test de connexion
            await self.client.ping()
            logger.info("✅ Connecté à Redis")
        except Exception as e:
            logger.error(f"❌ Erreur de connexion Redis: {e}")
            # Ne pas lever l'exception pour permettre le démarrage
            logger.warning("Redis non disponible, mais l'application continue")
    
    async def close(self):
        """Ferme la connexion Redis"""
        if self.client:
            await self.client.close()
            logger.info("🔌 Connexion Redis fermée")
    
    async def get_client(self) -> redis.Redis:
        """Retourne le client Redis"""
        if not self.client:
            await self.connect()
        return self.client
    
    async def get(self, key: str):
        """Récupère une valeur du cache"""
        if not self.client:
            return None
        
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"❌ Erreur Redis get: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = 300):
        """Stocke une valeur dans le cache"""
        if not self.client:
            return
        
        try:
            await self.client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"❌ Erreur Redis set: {e}")
    
    async def delete(self, key: str):
        """Supprime une clé du cache"""
        if not self.client:
            return
        
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"❌ Erreur Redis delete: {e}")

# Singleton pour l'application
redis_client = RedisClient()