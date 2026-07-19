"""Stateless document chunking service routines."""

def chunk_text_by_fixed_size(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size word chunks."""
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    if step <= 0:
        step = chunk_size
        
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        chunks.append(' '.join(chunk_words))
        
    return chunks

def create_document_chunks(document: dict, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """Create chunks from a document with index metadata."""
    text = document.get("content", "")
    chunks = chunk_text_by_fixed_size(text, chunk_size, overlap)
    
    return [{
        "id": f"{document.get('id', 'doc')}_chunk_{i}",
        "content": chunk,
        "metadata": {
            "source": document.get("source", "unknown"),
            "category": document.get("category", ""),
            "chunk_index": i
        }
    } for i, chunk in enumerate(chunks)]
