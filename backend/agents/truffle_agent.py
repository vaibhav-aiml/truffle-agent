"""Truffle Agent with RAG + Text-to-SQL - Works from any directory."""

import sys
import os

# Get the absolute path to the project root
_current_file = os.path.abspath(__file__)
_project_root = os.path.dirname(os.path.dirname(_current_file))

# Add to path if not already there
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Now import works
from backend.text_to_sql.converter import TextToSQL

class TruffleAgent:
    """Truffle with RAG and Text-to-SQL capabilities."""
    
    def __init__(self):
        print("🍄 Initializing Truffle with Text-to-SQL...")
        self.t2sql = TextToSQL()
        self._init_responses()
        print("✅ Truffle Agent ready!")
    
    def _init_responses(self):
        """Initialize knowledge base responses."""
        self.responses = {
            "invite": {
                "keywords": ["invite", "team member", "add member", "add person", "new member"],
                "answer": """
### How to Invite Team Members

**Step-by-Step Instructions:**

1. Log into your account dashboard
2. Click **Settings** in the sidebar
3. Select **Team** or **Team Members**
4. Click the **Invite Member** button
5. Enter the person's email address
6. Choose their role
7. Click **Send Invitation**

**Team Limits:**
- Basic: 5 members
- Premium: 20 members
- Enterprise: Unlimited
"""
            },
            "cancel": {
                "keywords": ["cancel", "unsubscribe", "stop billing", "end subscription"],
                "answer": """
### How to Cancel Your Subscription

**Steps:**
1. Go to **Settings** → **Billing**
2. Click **Cancel Subscription**
3. Confirm cancellation

**After cancellation:**
- Service continues until billing period ends
- No further charges
- Data kept for 30 days
"""
            },
            "mobile": {
                "keywords": ["mobile", "app", "phone", "ios", "android"],
                "answer": """
### Mobile App

**Download:**
- iOS: Apple App Store
- Android: Google Play Store

**Features:**
- Push notifications
- Reply to tickets
- Offline mode
"""
            },
            "password": {
                "keywords": ["password", "reset", "forgot"],
                "answer": """
### Reset Password

**Steps:**
1. Go to login page
2. Click **Forgot Password**
3. Enter your email
4. Check email for reset link
5. Create new password
"""
            },
            "subscription": {
                "keywords": ["subscription", "plan", "pricing", "basic", "premium", "enterprise"],
                "answer": """
### Subscription Plans

**Basic** - $9.99/month: 5 members, 100GB storage
**Premium** - $29.99/month: 20 members, 500GB storage, priority support
**Enterprise** - $99.99/month: Unlimited members, 2TB storage, 24/7 support

💡 Save 20% with annual billing!
"""
            },
            "refund": {
                "keywords": ["refund", "money back", "guarantee"],
                "answer": """
### Refund Policy

30-Day money-back guarantee. Request refund in Settings → Billing.
Processed in 5-7 business days.
"""
            }
        }
    
    def _get_rag_answer(self, query: str) -> dict:
        """Get answer from knowledge base."""
        query_lower = query.lower()
        
        for key, data in self.responses.items():
            for keyword in data["keywords"]:
                if keyword in query_lower:
                    return {
                        "response": data["answer"],
                        "confidence": 95,
                        "sources": ["Knowledge Base"]
                    }
        
        return {
            "response": "I couldn't find that. Try asking about invites, cancellation, mobile app, password reset, subscription plans, or refunds.",
            "confidence": 50,
            "sources": ["Default"]
        }
    
    def chat(self, query: str) -> dict:
        """Route to appropriate handler."""
        query_lower = query.lower()
        
        # Check if it's a database/ticket question
        db_keywords = ["ticket", "tickets", "open", "resolved", "priority", 
                       "assigned to", "satisfaction", "count tickets", "how many",
                       "show me", "list tickets"]
        
        is_db_query = any(keyword in query_lower for keyword in db_keywords)
        
        if is_db_query and hasattr(self, 't2sql'):
            try:
                result = self.t2sql.answer(query)
                return {
                    "query": query,
                    "response": result["answer"],
                    "confidence": 95,
                    "type": "sql",
                    "sql": result.get("sql"),
                    "sources": ["Database"]
                }
            except Exception as e:
                return {
                    "query": query,
                    "response": f"Database error: {e}",
                    "confidence": 50,
                    "type": "error",
                    "sources": []
                }
        else:
            rag_result = self._get_rag_answer(query)
            return {
                "query": query,
                "response": rag_result["response"],
                "confidence": rag_result["confidence"],
                "type": "rag",
                "sources": rag_result["sources"]
            }

if __name__ == "__main__":
    agent = TruffleAgent()
    
    test_queries = [
        "How do I invite team members?",
        "How many open tickets?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Q: {query}")
        result = agent.chat(query)
        print(f"A: {result['response'][:200]}...")
        print(f"Type: {result.get('type', 'unknown')}")
