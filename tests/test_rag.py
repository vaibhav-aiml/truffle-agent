"""Unit tests for the RAG and retrieval system components."""

import unittest
import sys
import os

# Set up module paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.rag.keyword_router import route_keyword_query
from backend.services.vector_service import get_embedding, calculate_cosine_similarity

class TestRAGComponents(unittest.TestCase):
    
    def test_keyword_router_valid_match(self):
        """Test that the route_keyword_query successfully parses password reset queries."""
        result = route_keyword_query("How to reset password?")
        
        self.assertGreater(result["confidence"], 0.8)
        self.assertEqual(result["source"], "Password Reset Guide")
        self.assertIn("Forgot Password", result["response"])

    def test_keyword_router_default_fallback(self):
        """Test router behavior when no matching keywords are provided."""
        result = route_keyword_query("Unrecognized query for testing defaults")
        
        self.assertEqual(result["confidence"], 0.3)
        self.assertEqual(result["source"], "Default")
        self.assertIn("contact support", result["response"].lower())

    def test_vector_store_offline_fallback(self):
        """Verify that the vector embedding and similarity function runs offline without API keys."""
        text = "Validate vector dimensions"
        
        # Test fallback embedding works and has correct shape (384 dimensions)
        embedding = get_embedding(None, text)
        self.assertEqual(len(embedding), 384)
        
        # Test cosine similarity output bounds
        similarity = calculate_cosine_similarity(embedding, embedding)
        self.assertAlmostEqual(similarity, 1.0, places=5)

if __name__ == "__main__":
    unittest.main()
