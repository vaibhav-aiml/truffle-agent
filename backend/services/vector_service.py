"""Stateless vector database and embedding operations service."""

import json
import os
import hashlib
import numpy as np
from pathlib import Path
from openai import OpenAI
from backend.utils.logger import logger

def create_openai_client(api_key: str = None) -> OpenAI | None:
    """Build an OpenAI API client instance if keys are configured."""
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OpenAI API key not found. Using local hash embedding fallback.")
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to create OpenAI client: {e}")
        return None

def get_embedding(client: OpenAI | None, text: str) -> list[float]:
    """Generate text embeddings. Falls back to deterministic hash embeddings if client is None."""
    if not client:
        # Deterministic fallback embedding representation
        embedding = [0.0] * 384
        for i, char in enumerate(text[:100]):
            hash_val = int(hashlib.md5(char.encode()).hexdigest(), 16) % 384
            embedding[hash_val] += 1.0
        norm = np.linalg.norm(embedding)
        return (embedding / norm).tolist() if norm > 0 else embedding

    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding error: {e}. Falling back to local hash.")
        return get_embedding(None, text)

def load_vector_db(storage_path: str = "data/processed/embeddings/") -> list[dict]:
    """Load vector database document list from disk."""
    file_path = Path(storage_path) / "vectors.json"
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                documents = json.load(f)
            logger.info(f"Loaded {len(documents)} documents from vector database at {file_path}.")
            return documents
        except Exception as e:
            logger.error(f"Failed to load vector DB from {file_path}: {e}")
    else:
        logger.info(f"No vector DB found at {file_path}. Initializing empty DB.")
    return []

def save_vector_db(storage_path: str, documents: list[dict]):
    """Save vector database document list to disk."""
    dir_path = Path(storage_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / "vectors.json"
    try:
        docs_to_save = []
        for doc in documents:
            doc_copy = doc.copy()
            # Ensure float type values are mapped for standard JSON serialization
            doc_copy["embedding"] = [float(x) for x in doc["embedding"]]
            docs_to_save.append(doc_copy)
        with open(file_path, "w") as f:
            json.dump(docs_to_save, f, indent=2)
        logger.info(f"Saved {len(documents)} documents to vector database at {file_path}.")
    except Exception as e:
        logger.error(f"Failed to save vector DB to {file_path}: {e}")

def calculate_cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate the cosine similarity between two numeric lists."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    dot = np.dot(a_arr, b_arr)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    return float(dot / (norm_a * norm_b + 1e-8))

def add_document_to_db(client: OpenAI | None, documents: list[dict], doc_id: str, content: str, source: str, category: str, storage_path: str = None) -> list[dict]:
    """Embed and append a document chunk to the vector list."""
    embedding = get_embedding(client, content)
    documents.append({
        "id": doc_id,
        "content": content,
        "metadata": {
            "source": source,
            "category": category
        },
        "embedding": embedding
    })
    if storage_path:
        save_vector_db(storage_path, documents)
    return documents

def search_vector_db(client: OpenAI | None, documents: list[dict], query: str, top_k: int = 3) -> list[dict]:
    """Retrieve top k most similar document records matching query."""
    if not client:
        # Local keyword-matching fallback search for offline running
        logger.info("OpenAI client missing. Performing local keyword search ranking fallback.")
        query_words = set(query.strip().lower().split())
        stop_words = {"what", "is", "your", "how", "do", "i", "the", "a", "an", "to", "for", "in", "of", "and", "we", "accept"}
        query_keywords = query_words - stop_words
        if not query_keywords:
            query_keywords = query_words
            
        results = []
        for doc in documents:
            doc_content_lower = doc["content"].lower()
            score = 0.0
            for keyword in query_keywords:
                count = doc_content_lower.count(keyword)
                if count > 0:
                    score += 1.0 + (0.1 * count)
                    
            similarity = min(0.99, score / max(1.0, len(query_keywords)))
            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "similarity": similarity
            })
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    query_embedding = get_embedding(client, query)
    results = []
    for doc in documents:
        similarity = calculate_cosine_similarity(query_embedding, doc["embedding"])
        results.append({
            "id": doc["id"],
            "content": doc["content"],
            "metadata": doc["metadata"],
            "similarity": similarity
        })
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]

