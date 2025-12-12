# src/utils/cache_manager.py
from typing import Optional, Any
import time

_logger = None
try:
    import redis
except Exception:
    redis = None

# Simple in-memory fallback
class _InMemoryCache:
    def __init__(self):
        self._store = {}  # key -> (value, expire_ts or None)

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        expire_ts = None if ex is None else time.time() + ex
        self._store[key] = (value, expire_ts)

    def get(self, key: str) -> Optional[Any]:
        val = self._store.get(key)
        if not val:
            return None
        value, expire_ts = val
        if expire_ts is not None and time.time() > expire_ts:
            del self._store[key]
            return None
        return value

    def delete(self, key: str):
        self._store.pop(key, None)

class CacheManager:
    """
    Thin wrapper: if redis available, uses it, otherwise in-memory.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        global _logger
        if _logger is None:
            from .logger import setup_logger
            _logger = setup_logger(__name__)
        self._logger = _logger

        if redis is not None:
            try:
                self._client = redis.Redis(host=host, port=port, db=db, socket_connect_timeout=1)
                # do a small ping to ensure connectivity (non-fatal)
                self._client.ping()
                self._logger.debug("Using redis cache backend")
                self._is_redis = True
            except Exception:
                self._logger.warning("Redis not available -> using in-memory cache fallback")
                self._client = _InMemoryCache()
                self._is_redis = False
        else:
            self._logger.debug("redis package not installed -> using in-memory cache")
            self._client = _InMemoryCache()
            self._is_redis = False

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        if self._is_redis:
            # redis accepts seconds expiry
            self._client.set(name=key, value=value, ex=ex)
        else:
            self._client.set(key, value, ex)

    def get(self, key: str) -> Optional[Any]:
        val = self._client.get(key)
        if self._is_redis and val is not None:
            # redis returns bytes; try decode
            try:
                return val.decode()
            except Exception:
                return val
        return val

    def delete(self, key: str):
        if self._is_redis:
            self._client.delete(key)
        else:
            self._client.delete(key)
