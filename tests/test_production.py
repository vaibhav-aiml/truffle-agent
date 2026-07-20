"""Unit tests for production readiness: caching, rate limiting, database pools, and SQL read-only enforcement."""

import unittest
import sys
import os
import time

# Set up module paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config import settings
from backend.services.cache_service import get_cached_query, set_cached_query, make_query_cache_key, clear_cache
from backend.services.rate_limiter import is_rate_limited, clear_rate_limits
from backend.services.sql_service import get_db_connection, execute_sql_query

class TestProductionServices(unittest.TestCase):
    
    def setUp(self):
        clear_cache()
        clear_rate_limits()
        
    def test_caching_fallback_operations(self):
        """Verify that the cache successfully saves and retrieves query payloads."""
        key = make_query_cache_key("Unique Query for Caching Test")
        payload = {"response": "Cached test response", "confidence": 99, "type": "sql"}
        
        # Ensure it starts empty
        self.assertIsNone(get_cached_query(key))
        
        # Set cache
        set_cached_query(key, payload)
        
        # Retrieve cache
        retrieved = get_cached_query(key)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["response"], "Cached test response")
        self.assertEqual(retrieved["confidence"], 99)

    def test_rate_limiting_sliding_window(self):
        """Test that the rate limiter blocks queries after exceeding threshold counts."""
        user_identifier = "test_client_ip_127_0_0_1"
        
        # Force a low limit parameters override for tests
        settings.RATE_LIMIT_MAX_REQUESTS = 3
        settings.RATE_LIMIT_WINDOW = 2
        
        # Hit 1, 2, 3 - Should not be limited
        self.assertFalse(is_rate_limited(user_identifier))
        self.assertFalse(is_rate_limited(user_identifier))
        self.assertFalse(is_rate_limited(user_identifier))
        
        # Hit 4 - Should exceed the limit and return True (limited)
        self.assertTrue(is_rate_limited(user_identifier))
        
        # Clear limits and verify it opens up again
        clear_rate_limits()
        self.assertFalse(is_rate_limited(user_identifier))

    def test_sqlite_wal_journal_mode(self):
        """Confirm that get_db_connection initializes SQLite with WAL mode enabled."""
        db_path = str(settings.DB_PATH)
        
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode;")
            mode = cursor.fetchone()[0]
            
        self.assertEqual(mode.lower(), "wal")


class TestSQLReadOnlyAuthorizer(unittest.TestCase):
    """Verify that the read-only authorizer blocks mutation operations."""
    
    def test_select_query_allowed(self):
        """A legitimate SELECT should succeed through the read-only connection."""
        db_path = str(settings.DB_PATH)
        result = execute_sql_query(db_path, "SELECT COUNT(*) FROM tickets")
        self.assertIsNone(result["error"])
        self.assertIsNotNone(result["data"])

    def test_select_with_aggregate_allowed(self):
        """SELECT with aggregate functions (AVG, COUNT) should work."""
        db_path = str(settings.DB_PATH)
        result = execute_sql_query(db_path, "SELECT AVG(satisfaction_score) FROM tickets WHERE satisfaction_score IS NOT NULL")
        self.assertIsNone(result["error"])

    def test_select_with_group_by_allowed(self):
        """SELECT with GROUP BY should work."""
        db_path = str(settings.DB_PATH)
        result = execute_sql_query(db_path, "SELECT status, COUNT(*) FROM tickets GROUP BY status")
        self.assertIsNone(result["error"])
        self.assertGreater(result["count"], 0)

    def test_insert_blocked(self):
        """INSERT should be blocked by the read-only authorizer."""
        db_path = str(settings.DB_PATH)
        result = execute_sql_query(db_path, "INSERT INTO tickets (id, customer_name) VALUES (999, 'Hacker')")
        self.assertIsNotNone(result["error"])
        self.assertIn("blocked", result["error"].lower())

    def test_update_blocked(self):
        """UPDATE should be blocked by the read-only authorizer."""
        db_path = str(settings.DB_PATH)
        result = execute_sql_query(db_path, "UPDATE tickets SET status = 'hacked' WHERE id = 1")
        self.assertIsNotNone(result["error"])
        self.assertIn("blocked", result["error"].lower())

    def test_delete_blocked(self):
        """DELETE should be blocked by the read-only authorizer."""
        db_path = str(settings.DB_PATH)
        result = execute_sql_query(db_path, "DELETE FROM tickets WHERE id = 1")
        self.assertIsNotNone(result["error"])
        self.assertIn("blocked", result["error"].lower())

    def test_drop_table_blocked(self):
        """DROP TABLE should be blocked by the read-only authorizer."""
        db_path = str(settings.DB_PATH)
        result = execute_sql_query(db_path, "DROP TABLE tickets")
        self.assertIsNotNone(result["error"])
        self.assertIn("blocked", result["error"].lower())

    def test_attach_database_blocked(self):
        """ATTACH DATABASE should be blocked by the read-only authorizer."""
        db_path = str(settings.DB_PATH)
        result = execute_sql_query(db_path, "ATTACH DATABASE ':memory:' AS hack_db")
        self.assertIsNotNone(result["error"])
        self.assertIn("blocked", result["error"].lower())

    def test_pragma_blocked(self):
        """PRAGMA should be blocked by the read-only authorizer."""
        db_path = str(settings.DB_PATH)
        result = execute_sql_query(db_path, "PRAGMA table_info(tickets)")
        self.assertIsNotNone(result["error"])
        self.assertIn("blocked", result["error"].lower())


if __name__ == "__main__":
    unittest.main()
