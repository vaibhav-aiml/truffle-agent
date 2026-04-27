"""Smart vector store with OpenAI embeddings."""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict
from backend.rag.openai_embeddings import OpenAIEmbeddings

class SmartVectorStore:
    """Vector store using OpenAI embeddings."""
    
    def __init__(self, storage_path: str = "data/processed/embeddings/"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.embeddings = OpenAIEmbeddings()
        self.documents = []
        self.load()
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        a = np.array(a)
        b = np.array(b)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot / (norm_a * norm_b + 1e-8)
    
    def add_document(self, document: Dict) -> str:
        doc_id = document.get("id", f"doc_{len(self.documents)}")
        content = document.get("content", "")
        
        print(f"  Embedding: {document.get('source', doc_id)}...")
        embedding = self.embeddings.embed(content)
        
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": {
                "source": document.get("source", "unknown"),
                "category": document.get("category", "general")
            },
            "embedding": embedding
        })
        
        self.save()
        return doc_id
    
    def add_documents(self, documents: List[Dict]) -> List[str]:
        return [self.add_document(doc) for doc in documents]
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        query_embedding = self.embeddings.embed(query)
        
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
    
    def count(self) -> int:
        return len(self.documents)
    
    def save(self):
        docs_to_save = []
        for doc in self.documents:
            doc_copy = doc.copy()
            doc_copy["embedding"] = [float(x) for x in doc["embedding"]]
            docs_to_save.append(doc_copy)
        
        with open(self.storage_path / "vectors.json", "w") as f:
            json.dump(docs_to_save, f, indent=2)
    
    def load(self):
        file_path = self.storage_path / "vectors.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                self.documents = json.load(f)
            print(f"✅ Loaded {len(self.documents)} documents")

if __name__ == "__main__":
    store = SmartVectorStore()
    print(f"✅ Smart vector store ready!")
