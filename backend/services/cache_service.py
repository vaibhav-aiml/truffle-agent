"""Stateless caching service supporting Redis and in-memory fallback."""

import json
import hashlib
from backend.config import settings
from backend.utils.logger import logger

# In-memory dictionary fallback cache
_local_cache = {}

# Try to initialize redis client
_redis_client = None
try:
    import redis
    # Set socket timeout to prevent blocking application if Redis is offline
    _redis_client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
    _redis_client.ping()
    logger.info(f"Connected to Redis cache server at: {settings.REDIS_URL}")
except ImportError:
    logger.warning("The 'redis' package is not installed. Caching will fall back to local in-memory dictionaries.")
    _redis_client = None
except Exception as e:
    logger.warning(f"Could not connect to Redis server: {e}. Caching will fall back to local in-memory dictionaries.")
    _redis_client = None

def make_query_cache_key(query: str) -> str:
    """Generate a unique deterministic cache key string from user queries."""
    clean_query = query.strip().lower()
    h = hashlib.sha256(clean_query.encode("utf-8")).hexdigest()
    return f"truffle:query:{h}"

def get_cached_query(key: str) -> dict | None:
    """Retrieve cache payload if present and valid."""
    if _redis_client:
        try:
            val = _redis_client.get(key)
            if val:
                return json.loads(val.decode("utf-8"))
        except Exception as e:
            logger.error(f"Redis cache read error: {e}")
    else:
        return _local_cache.get(key)
    return None

def set_cached_query(key: str, value: dict, ttl: int = None):
    """Save query answer payload to cache with a TTL (expiration)."""
    ttl = ttl or settings.CACHE_TTL
    if _redis_client:
        try:
            _redis_client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis cache write error: {e}")
    else:
        _local_cache[key] = value

def clear_cache():
    """Clear all cached records (useful for debugging and testing)."""
    global _local_cache
    if _redis_client:
        try:
            # Delete keys matching namespace prefix
            keys = _redis_client.keys("truffle:*")
            if keys:
                _redis_client.delete(*keys)
            logger.info("Cleared Redis cache database.")
        except Exception as e:
            logger.error(f"Failed to clear Redis cache: {e}")
    else:
        _local_cache.clear()
        logger.info("Cleared in-memory cache dictionary.")
