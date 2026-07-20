"""Shared Redis circuit breaker utility for connection resilience.

Provides a thread-safe circuit breaker that tracks Redis connection health
and implements a cooldown period after failures, preventing repeated
timeout delays from blocking user-facing requests.
"""

import time
import threading
from backend.utils.logger import logger


class RedisCircuitBreaker:
    """Thread-safe circuit breaker for Redis connections.

    When Redis is unreachable, the breaker trips into an 'offline' state
    and refuses further connection attempts for a configurable cooldown
    period (default 60 seconds). After the cooldown expires, the next
    check will attempt a single reconnect ping — recovering the breaker
    on success, or resetting the cooldown on failure.
    """

    def __init__(self, cooldown_seconds: float = 60.0, name: str = "Redis"):
        self._online: bool = True
        self._cooldown_until: float = 0.0
        self._cooldown_seconds: float = cooldown_seconds
        self._name: str = name
        self._lock: threading.Lock = threading.Lock()

    @property
    def is_online(self) -> bool:
        """Return the current connection status (not thread-safe snapshot)."""
        return self._online

    def check_status(self, client) -> bool:
        """Check whether Redis is available, respecting cooldown.

        Args:
            client: A Redis client instance with a `.ping()` method,
                    or None if no client was ever created.

        Returns:
            True if Redis is considered online and usable, False otherwise.
        """
        with self._lock:
            if self._online:
                return True

            # Still within cooldown window — skip the ping entirely.
            if time.time() <= self._cooldown_until:
                return False

            # Cooldown expired — attempt a reconnect.
            logger.info(f"{self._name} circuit breaker cooldown expired. Attempting reconnect...")
            try:
                if client is not None:
                    client.ping()
                    self._online = True
                    logger.info(f"Successfully reconnected to {self._name}.")
                    return True
                return False
            except Exception:
                self._cooldown_until = time.time() + self._cooldown_seconds
                return False

    def handle_failure(self) -> None:
        """Trip the breaker into 'offline' state and start cooldown.

        Safe to call multiple times — only the first call after recovery
        actually transitions state.
        """
        with self._lock:
            if self._online:
                logger.warning(
                    f"{self._name} operation failed. "
                    f"Activating {self._cooldown_seconds:.0f}-second cooldown circuit breaker."
                )
                self._online = False
                self._cooldown_until = time.time() + self._cooldown_seconds

    def force_offline(self) -> None:
        """Unconditionally mark the breaker as offline (used during init failures)."""
        with self._lock:
            self._online = False

    def reset(self) -> None:
        """Reset the breaker to online state (used in testing)."""
        with self._lock:
            self._online = True
            self._cooldown_until = 0.0
