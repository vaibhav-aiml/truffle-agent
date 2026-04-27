"""Retriever for Truffle RAG."""

from typing import List, Dict
from backend.rag.vector_store import SimpleVectorStore
from backend.rag.chunking import DocumentChunker, get_sample_documents

class Retriever:
    """Retrieve relevant documents."""
    
    def __init__(self):
        self.vector_store = SimpleVectorStore()
        self.chunker = DocumentChunker()
    
    def index_documents(self, documents: List[Dict]):
        """Index documents for search."""
        all_chunks = []
        for doc in documents:
            chunks = self.chunker.create_document_chunks(doc)
            all_chunks.extend(chunks)
        
        self.vector_store.add_documents(all_chunks)
        print(f"✅ Indexed {len(all_chunks)} chunks")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve relevant documents."""
        return self.vector_store.search(query, top_k)
    
    def retrieve_with_context(self, query: str, top_k: int = 3) -> Dict:
        """Retrieve with context for RAG."""
        docs = self.retrieve(query, top_k)
        return {
            "query": query,
            "documents": docs,
            "context": "\n\n".join([d["content"] for d in docs]),
            "sources": [d["metadata"].get("source", "unknown") for d in docs]
        }

def setup_knowledge_base():
    """Initialize with sample documents."""
    retriever = Retriever()
    retriever.index_documents(get_sample_documents())
    return retriever

if __name__ == "__main__":
    print("🔧 Setting up knowledge base...")
    retriever = setup_knowledge_base()
    
    # Test queries
    test_queries = [
        "How do I reset my password?",
        "What are your subscription plans?",
        "How do I get a refund?"
    ]
    
    for query in test_queries:
        result = retriever.retrieve_with_context(query)
        print(f"\n🔍 Query: {query}")
        print(f"   Found: {len(result['documents'])} documents")
        if result['documents']:
            print(f"   Best match similarity: {result['documents'][0]['similarity']:.3f}")
    
    print("\n✅ RAG system ready!")
