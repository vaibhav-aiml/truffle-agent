"""Rebuild Truffle with 12+ knowledge base documents."""

import shutil
from pathlib import Path

# Clear old data
vectors_file = Path("data/processed/embeddings/vectors.json")
if vectors_file.exists():
    vectors_file.unlink()
    print("✅ Cleared old vectors")

print("\n📚 Building Truffle knowledge base with 12 documents...")
print("="*60)

from backend.rag.smart_vector_store import SmartVectorStore
from backend.rag.expanded_kb import get_expanded_kb

store = SmartVectorStore()
documents = get_expanded_kb()

for i, doc in enumerate(documents, 1):
    store.add_document(doc)
    print(f"  {i}. Added: {doc['source']}")

print(f"\n✅ Success! Indexed {store.count()} documents")
print(f"📊 Total chunks: {len(store.documents)}")

# Test search quality
print("\n🔍 Testing search quality...")
test_queries = [
    "How do I invite team members?",
    "What happens if I cancel my subscription?",
    "How do I use the mobile app?"
]

for query in test_queries:
    results = store.search(query, top_k=1)
    if results:
        print(f"\n  Q: {query}")
        print(f"  Found: {results[0]['metadata']['source']}")
        print(f"  Similarity: {results[0]['similarity']:.3f}")
