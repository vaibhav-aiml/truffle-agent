"""Stateless user request rate limiter service supporting Redis and local dictionary fallback."""

import time
from backend.config import settings
from backend.utils.logger import logger

# In-memory sliding window fallback tracking
# Structure: { "ip_or_user": [timestamp1, timestamp2, ...] }
_local_limits = {}

# Try to use the initialized Redis client if available
_redis_client = None
try:
    import redis
    _redis_client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
    _redis_client.ping()
except Exception:
    # Silent warning as cache_service already logs the state
    _redis_client = None

def is_rate_limited(identifier: str) -> bool:
    """Verify if a user identifier (IP or username) exceeds query rate limit parameters.
    
    Returns:
        True if limited (blocked), False otherwise.
    """
    now = time.time()
    window = settings.RATE_LIMIT_WINDOW
    limit = settings.RATE_LIMIT_MAX_REQUESTS
    
    # 1. Use Redis Fixed-Window Rate Limiting
    if _redis_client:
        key = f"truffle:ratelimit:{identifier}:{int(now / window)}"
        try:
            current = _redis_client.get(key)
            if current and int(current) >= limit:
                logger.warning(f"Rate limit hit for user: {identifier} (Redis count={current})")
                return True
                
            # Increment and set TTL
            pipe = _redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            pipe.execute()
            return False
        except Exception as e:
            logger.error(f"Redis rate limit read error: {e}. Falling back to in-memory check.")
            
    # 2. In-Memory Sliding Window Fallback
    global _local_limits
    user_hits = _local_limits.get(identifier, [])
    
    # Clean timestamps older than current window range
    threshold = now - window
    user_hits = [t for t in user_hits if t > threshold]
    
    if len(user_hits) >= limit:
        logger.warning(f"Rate limit hit for user: {identifier} (Memory count={len(user_hits)})")
        return True
        
    # Log current hit
    user_hits.append(now)
    _local_limits[identifier] = user_hits
    return False

def clear_rate_limits():
    """Clear all rate limits records."""
    global _local_limits
    if _redis_client:
        try:
            keys = _redis_client.keys("truffle:ratelimit:*")
            if keys:
                _redis_client.delete(*keys)
            logger.info("Cleared Redis rate limit metrics.")
        except Exception as e:
            logger.error(f"Failed to clear Redis rate limits: {e}")
    else:
        _local_limits.clear()
        logger.info("Cleared in-memory rate limit logs.")
