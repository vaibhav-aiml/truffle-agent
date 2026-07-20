"""Stateless user request rate limiter service supporting Redis and local dictionary fallback."""

import time
import threading
from backend.config import settings
from backend.utils.logger import logger
from backend.utils.circuit_breaker import RedisCircuitBreaker


class ThreadSafeBoundedRateLimiter:
    """Thread-safe rate limiter tracking state with limit on tracked identifiers to prevent memory leaks."""
    def __init__(self, max_users: int = 5000):
        self.max_users: int = max_users
        self.limits: dict[str, list[float]] = {}
        self.lock: threading.Lock = threading.Lock()

    def check_and_add(self, identifier: str, limit: int, window: float) -> bool:
        """Check if identifier exceeds the rate limit and record the current request.

        Returns:
            True if rate-limited (blocked), False if allowed.
        """
        now = time.time()
        threshold = now - window
        with self.lock:
            # Clean up old users if tracking state gets too large
            if len(self.limits) >= self.max_users and identifier not in self.limits:
                inactive_users: list[str] = []
                for user, hits in list(self.limits.items()):
                    cleaned_hits = [t for t in hits if t > threshold]
                    if not cleaned_hits:
                        inactive_users.append(user)
                    else:
                        self.limits[user] = cleaned_hits
                
                for user in inactive_users:
                    del self.limits[user]
                
                # Hard limit cap eviction if still over limit
                if len(self.limits) >= self.max_users:
                    arbitrary_user = next(iter(self.limits))
                    del self.limits[arbitrary_user]

            user_hits = self.limits.get(identifier, [])
            user_hits = [t for t in user_hits if t > threshold]
            
            if len(user_hits) >= limit:
                self.limits[identifier] = user_hits
                return True
                
            user_hits.append(now)
            self.limits[identifier] = user_hits
            return False

    def clear(self) -> None:
        with self.lock:
            self.limits.clear()

# Initialize local limits tracking
_local_limits = ThreadSafeBoundedRateLimiter(max_users=5000)

# Shared circuit breaker instance for the rate limiter service
_circuit_breaker = RedisCircuitBreaker(cooldown_seconds=60.0, name="Redis-RateLimit")
_redis_client = None

try:
    import redis
    _redis_client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
    _redis_client.ping()
except Exception:
    # Silent warning as cache_service already logs the state
    _redis_client = None
    _circuit_breaker.force_offline()

def is_rate_limited(identifier: str) -> bool:
    """Verify if a user identifier (IP or username) exceeds query rate limit parameters.
    
    Returns:
        True if limited (blocked), False otherwise.
    """
    now = time.time()
    window: float = settings.RATE_LIMIT_WINDOW
    limit: int = settings.RATE_LIMIT_MAX_REQUESTS
    
    # 1. Use Redis Fixed-Window Rate Limiting
    if _redis_client and _circuit_breaker.check_status(_redis_client):
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
            _circuit_breaker.handle_failure()
            
    # 2. In-Memory Sliding Window Fallback
    is_limited = _local_limits.check_and_add(identifier, limit, window)
    if is_limited:
         logger.warning(f"Rate limit hit for user: {identifier} (Memory limit exceeded)")
    return is_limited

def clear_rate_limits() -> None:
    """Clear all rate limits records."""
    _local_limits.clear()
    if _redis_client and _circuit_breaker.check_status(_redis_client):
        try:
            keys = _redis_client.keys("truffle:ratelimit:*")
            if keys:
                _redis_client.delete(*keys)
            logger.info("Cleared Redis rate limit metrics.")
        except Exception as e:
            logger.error(f"Failed to clear Redis rate limits: {e}")
            _circuit_breaker.handle_failure()
    else:
        logger.info("Cleared in-memory rate limit logs.")
