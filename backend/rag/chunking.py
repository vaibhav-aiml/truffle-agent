"""Document chunking for Truffle RAG."""

from typing import List, Dict

class DocumentChunker:
    """Split documents into searchable chunks."""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_by_fixed_size(self, text: str) -> List[str]:
        """Split text into fixed-size chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunks.append(' '.join(chunk_words))
        
        return chunks
    
    def create_document_chunks(self, document: Dict) -> List[Dict]:
        """Create chunks with metadata."""
        text = document.get("content", "")
        chunks = self.chunk_by_fixed_size(text)
        
        return [{
            "id": f"{document.get('id', 'doc')}_chunk_{i}",
            "content": chunk,
            "metadata": {
                "source": document.get("source", "unknown"),
                "category": document.get("category", ""),
                "chunk_index": i
            }
        } for i, chunk in enumerate(chunks)]

# Sample knowledge base
SAMPLE_DOCUMENTS = [
    {
        "id": "doc_001",
        "source": "password_reset.md",
        "category": "account",
        "content": """
        How to Reset Your Password:
        1. Click 'Forgot Password' on the login page
        2. Enter your email address
        3. Check your email for a reset link
        4. Click the link and create a new password
        Passwords must be at least 8 characters long.
        """
    },
    {
        "id": "doc_002",
        "source": "subscription_plans.md",
        "category": "billing",
        "content": """
        Our Subscription Plans:
        - Basic: $9.99/month, 5 team members, 100GB storage
        - Premium: $29.99/month, 20 team members, 500GB storage
        - Enterprise: $99.99/month, unlimited team members, 2TB storage
        Save 20% with annual billing.
        """
    },
    {
        "id": "doc_003",
        "source": "refund_policy.md",
        "category": "billing",
        "content": """
        Refund Policy:
        We offer a 30-day money-back guarantee on all plans.
        To request a refund, go to Billing Settings and click 'Request Refund'.
        Refunds are processed within 5-7 business days.
        """
    },
    {
        "id": "doc_004",
        "source": "api_docs.md",
        "category": "developer",
        "content": """
        API Documentation:
        Authentication: Bearer token
        Rate limits: 1000 requests per minute
        Endpoints: GET /users, POST /tickets, GET /tickets/{id}
        """
    }
]

def get_sample_documents():
    return SAMPLE_DOCUMENTS

if __name__ == "__main__":
    chunker = DocumentChunker()
    print("✅ Document chunker ready")
    for doc in get_sample_documents():
        chunks = chunker.create_document_chunks(doc)
        print(f"  {doc['source']}: {len(chunks)} chunks")
