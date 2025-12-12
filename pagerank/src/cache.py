from redis import Redis
from src.core.config import settings
import redis

# Utilisez redis_url au lieu de redis_host et redis_port
def get_redis_client():
    return Redis.from_url(settings.redis_url)

_cache = get_redis_client()

# Ou si vous voulez garder la même structure :
# parsed_url = redis.connection.parse_url(settings.redis_url)
# _cache = Redis(host=parsed_url['host'], port=parsed_url['port'], db=parsed_url['db'])

def save(key, value, expire=None):
    try:
        if expire:
            _cache.setex(key, expire, value)
        else:
            _cache.set(key, value)
        return True
    except Exception as e:
        print(f"Error saving to cache: {e}")
        return False

def get(key):
    try:
        return _cache.get(key)
    except Exception as e:
        print(f"Error getting from cache: {e}")
        return None