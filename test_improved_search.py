"""Test the improved search."""

from backend.rag.smart_vector_store import SmartVectorStore

store = SmartVectorStore()

test_queries = [
    "How do I invite team members?",
    "How do I add someone to my account?",
    "How do I cancel my subscription?",
    "Is there a mobile app?",
]

print("🔍 TESTING IMPROVED SEARCH")
print("="*60)

for query in test_queries:
    print(f"\nQ: {query}")
    results = store.search(query, top_k=1)
    
    if results:
        print(f"✅ Found: {results[0]['metadata']['source']}")
        print(f"   Similarity: {results[0]['similarity']:.3f}")
        print(f"   Preview: {results[0]['content'][:100]}...")
    else:
        print("❌ No results found")
    
    print("-"*40)
