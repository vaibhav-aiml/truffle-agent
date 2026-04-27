"""Check documents in vector store."""

from backend.rag.vector_store import SimpleVectorStore

store = SimpleVectorStore()
print(f"Total documents: {store.count()}")
print("\nAll documents in store:")

for i, doc in enumerate(store.documents):
    print(f"\n--- Document {i+1} ---")
    print(f"ID: {doc['id']}")
    print(f"Content preview: {doc['content'][:150]}...")
    print(f"Metadata: {doc['metadata']}")
