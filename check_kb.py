"""Check Truffle knowledge base."""

from backend.rag.smart_vector_store import SmartVectorStore

store = SmartVectorStore()
print(f"📚 Total documents in knowledge base: {store.count()}")
print("\n📂 Documents by source:")

for i, doc in enumerate(store.documents, 1):
    source = doc["metadata"].get("source", "unknown")
    print(f"  {i}. {source}")
