"""Keyword-based routing service for support queries.

Routes queries to pre-defined FAQ answers by matching keywords against a
rule table. Each rule maps to a document ID in the consolidated knowledge
base (expanded_kb.py), so the answer text is always fetched from the
single source of truth rather than maintained as a separate hardcoded copy.
"""

from backend.rag.expanded_kb import get_kb_by_id

# Each rule maps keywords → a KB document ID and a human-readable source label.
# The actual answer content is fetched dynamically from expanded_kb.py at query
# time, preventing content drift between the keyword router and the vector store.
RULES: list[dict] = [
    {
        "keywords": ["invite", "inviting", "add member", "team member", "add person", "new member", "add someone"],
        "doc_id": "doc_003",
        "source": "Team Management Guide"
    },
    {
        "keywords": ["cancel", "cancellation", "unsubscribe", "stop billing", "end subscription"],
        "doc_id": "doc_012",
        "source": "Cancellation Guide"
    },
    {
        "keywords": ["mobile app", "phone app", "ios app", "android app", "download app"],
        "doc_id": "doc_009",
        "source": "Mobile App Guide"
    },
    {
        "keywords": ["password", "reset password", "forgot password"],
        "doc_id": "doc_014",
        "source": "Password Reset Guide"
    },
    {
        "keywords": ["refund", "money back", "get refund"],
        "doc_id": "doc_016",
        "source": "Refund Policy"
    },
    {
        "keywords": ["subscription", "plans", "pricing", "basic", "premium", "enterprise"],
        "doc_id": "doc_015",
        "source": "Subscription Plans"
    },
    {
        "keywords": ["payment", "payment method", "pay", "visa", "paypal", "credit card"],
        "doc_id": "doc_013",
        "source": "Payment Methods"
    }
]


def route_keyword_query(query: str) -> dict:
    """Route queries to predefined policy answers based on exact keyword inclusion.

    Looks up the answer content from the consolidated knowledge base by document
    ID, ensuring the keyword router and vector search always serve identical text.
    """
    query_lower = query.lower()
    
    for rule in RULES:
        for keyword in rule["keywords"]:
            if keyword in query_lower:
                doc = get_kb_by_id(rule["doc_id"])
                if doc:
                    return {
                        "response": doc["content"],
                        "source": rule["source"],
                        "confidence": 0.95
                    }
                # Fallback if doc_id is misconfigured — should not happen.
                break
                
    return {
        "response": "I'm not sure about that. Please contact support for help.",
        "source": "Default",
        "confidence": 0.3
    }
