"""Simple vector store for Truffle."""

import json
import hashlib
from pathlib import Path
from typing import List, Dict

class SimpleVectorStore:
    """Local vector store with dummy embeddings."""
    
    def __init__(self, storage_path: str = "data/processed/embeddings/"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.documents = []
        self.load()
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create a simple hash-based embedding."""
        words = text.lower().split()
        embedding = [0.0] * 384
        
        for word in words[:50]:
            hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16) % 384
            embedding[hash_val] += 1
        
        norm = sum(x*x for x in embedding)**0.5
        return [x/norm for x in embedding] if norm > 0 else embedding
    
    def add_document(self, document: Dict) -> str:
        """Add a document to the store."""
        doc_id = document.get("id", f"doc_{len(self.documents)}")
        content = document.get("content", "")
        
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": document.get("metadata", {}),
            "embedding": self._create_embedding(content)
        })
        
        self.save()
        return doc_id
    
    def add_documents(self, documents: List[Dict]) -> List[str]:
        """Add multiple documents."""
        return [self.add_document(doc) for doc in documents]
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for similar documents."""
        query_embedding = self._create_embedding(query)
        
        results = []
        for doc in self.documents:
            similarity = self._cosine_similarity(query_embedding, doc["embedding"])
            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "similarity": similarity
            })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity."""
        dot = sum(x*y for x,y in zip(a,b))
        norm_a = sum(x*x for x in a)**0.5
        norm_b = sum(x*x for x in b)**0.5
        return dot/(norm_a*norm_b) if norm_a and norm_b else 0
    
    def count(self) -> int:
        """Return number of documents in the store."""
        return len(self.documents)
    
    def save(self):
        """Save to disk."""
        with open(self.storage_path / "vectors.json", "w") as f:
            json.dump(self.documents, f, indent=2)
    
    def load(self):
        """Load from disk."""
        file_path = self.storage_path / "vectors.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                self.documents = json.load(f)
            print(f"✅ Loaded {len(self.documents)} documents")
        else:
            print("📭 No existing vector store found. Starting fresh.")

if __name__ == "__main__":
    store = SimpleVectorStore()
    print(f"✅ Vector store ready. Count: {store.count()}")
