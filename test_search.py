"""Test search across knowledge base."""

from backend.rag.smart_vector_store import SmartVectorStore

store = SmartVectorStore()

test_queries = [
    "How do I invite team members?",
    "How do I cancel my subscription?",
    "Do you have a mobile app?",
    "How do I export my data?",
    "What API authentication do you use?"
]

print("🔍 Testing search across knowledge base:\n")
print("="*60)

for query in test_queries:
    results = store.search(query, top_k=1)
    if results:
        source = results[0]["metadata"].get("source", "unknown")
        similarity = results[0]["similarity"]
        print(f"✅ Query: {query}")
        print(f"   Source: {source}")
        print(f"   Similarity: {similarity:.3f}")
    else:
        print(f"❌ Query: {query} → No results found")
    print()

print("="*60)
