"""OpenAI embeddings for Truffle - Lightweight and accurate."""

import os
from openai import OpenAI
from typing import List
import numpy as np

class OpenAIEmbeddings:
    """Real embeddings using OpenAI API."""
    
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = "text-embedding-3-small"
        
        if not self.api_key:
            print("⚠️ OpenAI API key not found. Using fallback mode.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            print(f"✅ OpenAI embeddings ready! Model: {self.model}")
    
    def embed(self, text: str) -> List[float]:
        """Create embedding for a single text."""
        if not self.client:
            return self._fake_embedding(text)
        
        response = self.client.embeddings.create(
            model=self.model,
            input=text[:8000]  # Truncate long texts
        )
        return response.data[0].embedding
    
    def _fake_embedding(self, text: str) -> List[float]:
        """Fallback embedding when no API key."""
        import hashlib
        embedding = [0.0] * 384
        for i, char in enumerate(text[:100]):
            hash_val = int(hashlib.md5(char.encode()).hexdigest(), 16) % 384
            embedding[hash_val] += 1
        norm = np.linalg.norm(embedding)
        return (embedding / norm).tolist() if norm > 0 else embedding

if __name__ == "__main__":
    emb = OpenAIEmbeddings()
    result = emb.embed("What payment methods do you accept?")
    print(f"Embedding created! Dimension: {len(result)}")
