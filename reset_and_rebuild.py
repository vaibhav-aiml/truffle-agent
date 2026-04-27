"""Reset and rebuild Truffle knowledge base."""

import shutil
from pathlib import Path

# Clear old data
paths_to_clear = [
    "data/processed/embeddings/vectors.json",
    "data/processed/chunks"
]

for path in paths_to_clear:
    p = Path(path)
    if p.exists():
        if p.is_file():
            p.unlink()
            print(f"Deleted: {path}")
        elif p.is_dir():
            shutil.rmtree(p)
            p.mkdir(parents=True)
            print(f"Cleared: {path}")

print("\n✅ Ready for fresh indexing!")

# Now rebuild with complete knowledge base
from backend.rag.retriever import Retriever
from backend.rag.complete_kb import get_knowledge_base
from backend.rag.chunking import DocumentChunker

print("\n🔄 Indexing knowledge base...")
retriever = Retriever()
chunker = DocumentChunker(chunk_size=300, overlap=50)
docs = get_knowledge_base()

all_chunks = []
for doc in docs:
    chunks = chunker.create_document_chunks(doc)
    all_chunks.extend(chunks)
    print(f"  {doc['source']}: {len(chunks)} chunks")

retriever.vector_store.add_documents(all_chunks)
print(f"\n✅ Indexed {len(all_chunks)} total chunks!")
