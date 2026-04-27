"""Test retrieval quality."""

from backend.rag.vector_store import SimpleVectorStore

store = SimpleVectorStore()

test_queries = [
    "What payment methods do you accept?",
    "How do I reset my password?",
    "What subscription plans do you offer?",
    "How do I get a refund?"
]

print("=" * 70)
print("Testing Truffle Retrieval")
print("=" * 70)

for query in test_queries:
    print(f"\n🔍 Query: {query}")
    results = store.search(query, top_k=2)
    
    if results:
        print(f"✅ Found {len(results)} results")
        for i, result in enumerate(results):
            print(f"\n   Result {i+1} (Similarity: {result['similarity']:.3f})")
            print(f"   Source: {result['metadata'].get('source', 'unknown')}")
            print(f"   Content: {result['content'][:200]}...")
    else:
        print("❌ No results found")
    
    print("-" * 70)
