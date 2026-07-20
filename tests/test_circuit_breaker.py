"""Unit tests for the shared Redis circuit breaker utility."""

import unittest
import sys
import os
import time
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.circuit_breaker import RedisCircuitBreaker


class TestRedisCircuitBreaker(unittest.TestCase):
    """Direct unit coverage for the RedisCircuitBreaker state machine."""

    def test_initial_state_is_online(self):
        """A fresh breaker should report online."""
        cb = RedisCircuitBreaker(cooldown_seconds=60.0, name="TestRedis")
        self.assertTrue(cb.is_online)

    def test_check_status_returns_true_when_online(self):
        """check_status should return True without pinging when already online."""
        cb = RedisCircuitBreaker(name="TestRedis")
        mock_client = MagicMock()
        self.assertTrue(cb.check_status(mock_client))
        # Should NOT have pinged — no reconnect needed when online.
        mock_client.ping.assert_not_called()

    def test_handle_failure_trips_breaker_offline(self):
        """After handle_failure, the breaker should be offline."""
        cb = RedisCircuitBreaker(cooldown_seconds=60.0, name="TestRedis")
        cb.handle_failure()
        self.assertFalse(cb.is_online)

    def test_check_status_returns_false_during_cooldown(self):
        """During cooldown, check_status should return False without pinging."""
        cb = RedisCircuitBreaker(cooldown_seconds=60.0, name="TestRedis")
        cb.handle_failure()

        mock_client = MagicMock()
        result = cb.check_status(mock_client)

        self.assertFalse(result)
        mock_client.ping.assert_not_called()

    def test_cooldown_expiry_triggers_reconnect_success(self):
        """After cooldown expires, a successful ping should recover the breaker."""
        cb = RedisCircuitBreaker(cooldown_seconds=0.1, name="TestRedis")
        cb.handle_failure()

        # Wait for cooldown to expire.
        time.sleep(0.15)

        mock_client = MagicMock()
        mock_client.ping.return_value = True

        result = cb.check_status(mock_client)
        self.assertTrue(result)
        self.assertTrue(cb.is_online)
        mock_client.ping.assert_called_once()

    def test_cooldown_expiry_triggers_reconnect_failure(self):
        """After cooldown expires, a failed ping should re-arm the cooldown."""
        cb = RedisCircuitBreaker(cooldown_seconds=0.1, name="TestRedis")
        cb.handle_failure()

        time.sleep(0.15)

        mock_client = MagicMock()
        mock_client.ping.side_effect = ConnectionError("Redis still down")

        result = cb.check_status(mock_client)
        self.assertFalse(result)
        self.assertFalse(cb.is_online)

        # Should still be blocked immediately after re-arm.
        result2 = cb.check_status(mock_client)
        self.assertFalse(result2)

    def test_handle_failure_is_idempotent(self):
        """Multiple handle_failure calls should not re-extend cooldown."""
        cb = RedisCircuitBreaker(cooldown_seconds=60.0, name="TestRedis")
        cb.handle_failure()
        self.assertFalse(cb.is_online)

        # Second call should be a no-op (already offline).
        cb.handle_failure()
        self.assertFalse(cb.is_online)

    def test_force_offline(self):
        """force_offline should mark breaker as offline unconditionally."""
        cb = RedisCircuitBreaker(name="TestRedis")
        self.assertTrue(cb.is_online)
        cb.force_offline()
        self.assertFalse(cb.is_online)

    def test_reset_restores_online(self):
        """reset should restore the breaker to online state."""
        cb = RedisCircuitBreaker(name="TestRedis")
        cb.handle_failure()
        self.assertFalse(cb.is_online)
        cb.reset()
        self.assertTrue(cb.is_online)

    def test_check_status_with_none_client_returns_false(self):
        """If no client was ever created, check_status should return False after cooldown."""
        cb = RedisCircuitBreaker(cooldown_seconds=0.01, name="TestRedis")
        cb.handle_failure()
        time.sleep(0.02)
        result = cb.check_status(None)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
