"""Stateless caching service supporting Redis and in-memory fallback."""

import json
import hashlib
import time
import threading
from backend.config import settings
from backend.utils.logger import logger
from backend.utils.circuit_breaker import RedisCircuitBreaker

class ThreadSafeBoundedTTLCache:
    """A thread-safe, size-limited in-memory dictionary cache with TTL expiration."""
    def __init__(self, maxsize: int = 1000, default_ttl: int = 86400):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self.cache: dict[str, tuple[dict, float]] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> dict | None:
        with self.lock:
            if key not in self.cache:
                return None
            val, expires = self.cache[key]
            if time.time() > expires:
                del self.cache[key]
                return None
            return val

    def set(self, key: str, value: dict, ttl: int | None = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        expires = time.time() + ttl
        with self.lock:
            # Enforce cache size limits
            if len(self.cache) >= self.maxsize and key not in self.cache:
                now = time.time()
                # Prune expired keys first
                expired_keys = [k for k, (_, exp) in self.cache.items() if now > exp]
                for k in expired_keys:
                    del self.cache[k]
                
                # If still over limit, evict the oldest inserted key
                if len(self.cache) >= self.maxsize:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    
            self.cache[key] = (value, expires)

    def clear(self) -> None:
        with self.lock:
            self.cache.clear()

# Initialize thread-safe local cache
_local_cache = ThreadSafeBoundedTTLCache(maxsize=1000, default_ttl=settings.CACHE_TTL)

# Shared circuit breaker instance for the cache service
_circuit_breaker = RedisCircuitBreaker(cooldown_seconds=60.0, name="Redis-Cache")
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
    _circuit_breaker.force_offline()
except Exception as e:
    logger.warning(f"Could not connect to Redis server: {e}. Caching will fall back to local in-memory dictionaries.")
    _redis_client = None
    _circuit_breaker.force_offline()

def make_query_cache_key(query: str) -> str:
    """Generate a unique deterministic cache key string from user queries."""
    clean_query = query.strip().lower()
    h = hashlib.sha256(clean_query.encode("utf-8")).hexdigest()
    return f"truffle:query:{h}"

def get_cached_query(key: str) -> dict | None:
    """Retrieve cache payload if present and valid."""
    if _redis_client and _circuit_breaker.check_status(_redis_client):
        try:
            val = _redis_client.get(key)
            if val:
                return json.loads(val.decode("utf-8"))
        except Exception as e:
            logger.error(f"Redis cache read error: {e}")
            _circuit_breaker.handle_failure()
            
    return _local_cache.get(key)

def set_cached_query(key: str, value: dict, ttl: int | None = None) -> None:
    """Save query answer payload to cache with a TTL (expiration)."""
    ttl = ttl or settings.CACHE_TTL
    if _redis_client and _circuit_breaker.check_status(_redis_client):
        try:
            _redis_client.setex(key, ttl, json.dumps(value))
            return
        except Exception as e:
            logger.error(f"Redis cache write error: {e}")
            _circuit_breaker.handle_failure()
            
    _local_cache.set(key, value, ttl)

def clear_cache() -> None:
    """Clear all cached records (useful for debugging and testing)."""
    _local_cache.clear()
    if _redis_client and _circuit_breaker.check_status(_redis_client):
        try:
            keys = _redis_client.keys("truffle:*")
            if keys:
                _redis_client.delete(*keys)
            logger.info("Cleared Redis cache database.")
        except Exception as e:
            logger.error(f"Failed to clear Redis cache: {e}")
            _circuit_breaker.handle_failure()
    else:
        logger.info("Cleared in-memory cache dictionary.")
