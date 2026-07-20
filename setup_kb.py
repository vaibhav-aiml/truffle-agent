"""Setup script to index knowledge base documents into the vector database."""

import os
from pathlib import Path
from backend.config import settings
from backend.services.vector_service import add_document_to_db, create_openai_client, save_vector_db

def run_knowledge_base_setup():
    storage_path = str(settings.VECTOR_DB_DIR)
    vectors_file = Path(storage_path) / "vectors.json"
    
    print(f"Initializing knowledge base at: {storage_path}")
    
    if vectors_file.exists():
        try:
            vectors_file.unlink()
            print("  Cleared old vector embeddings file.")
        except Exception as e:
            print(f"  Warning: could not delete old vector database file: {e}")
            
    openai_client = create_openai_client()
    documents = []
    
    from backend.rag.expanded_kb import EXPANDED_KB
    
    print("  Creating vector embeddings for documents...")
    for doc in EXPANDED_KB:
        print(f"    - Embedding: {doc['source']}")
        documents = add_document_to_db(
            openai_client, 
            documents, 
            doc_id=doc["id"], 
            content=doc["content"], 
            source=doc["source"], 
            category=doc["category"]
        )
        
    save_vector_db(storage_path, documents)
    print(f"\n[OK] Knowledge base setup complete! Indexed {len(documents)} documents.")

if __name__ == "__main__":
    run_knowledge_base_setup()
