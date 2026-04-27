"""Run Truffle Agent - Run this from truffle-agent folder."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

print(f"Project root: {os.getcwd()}")

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
                "answer": "How to invite team members: Go to Settings → Team → Invite Member. Enter email, choose role (Admin/Member/Viewer), send invitation."
            },
            "cancel": {
                "keywords": ["cancel", "unsubscribe", "stop billing"],
                "answer": "To cancel subscription: Go to Settings → Billing → Cancel Subscription. Service continues until billing period ends."
            },
            "mobile": {
                "keywords": ["mobile", "app", "phone", "ios", "android"],
                "answer": "Mobile app available on iOS App Store and Google Play Store. Features: push notifications, reply to tickets, offline mode."
            },
            "password": {
                "keywords": ["password", "reset", "forgot"],
                "answer": "To reset password: Click 'Forgot Password' on login page, enter email, check inbox for reset link, create new password."
            },
            "subscription": {
                "keywords": ["subscription", "plan", "pricing", "basic", "premium", "enterprise"],
                "answer": "Plans: Basic $9.99/mo (5 members), Premium $29.99/mo (20 members, priority support), Enterprise $99.99/mo (unlimited, 24/7 support). Save 20% with annual billing."
            },
            "refund": {
                "keywords": ["refund", "money back", "guarantee"],
                "answer": "30-day money-back guarantee. Request refund in Settings → Billing. Processed in 5-7 business days."
            }
        }
    
    def _get_rag_answer(self, query: str) -> dict:
        query_lower = query.lower()
        for key, data in self.responses.items():
            for keyword in data["keywords"]:
                if keyword in query_lower:
                    return {"response": data["answer"], "confidence": 95, "sources": ["Knowledge Base"]}
        return {"response": "I couldn't find that. Try asking about invites, cancellation, plans, password reset, refunds, or mobile app.", "confidence": 50, "sources": []}
    
    def chat(self, query: str) -> dict:
        query_lower = query.lower()
        db_keywords = ["ticket", "tickets", "open", "resolved", "priority", "assigned", "satisfaction", "how many", "show me"]
        
        if any(kw in query_lower for kw in db_keywords):
            try:
                result = self.t2sql.answer(query)
                return {"query": query, "response": result["answer"], "confidence": 95, "type": "sql", "sql": result.get("sql"), "sources": ["Database"]}
            except Exception as e:
                return {"query": query, "response": f"Database error: {e}", "confidence": 50, "type": "error"}
        else:
            rag = self._get_rag_answer(query)
            return {"query": query, "response": rag["response"], "confidence": rag["confidence"], "type": "rag", "sources": rag["sources"]}

if __name__ == "__main__":
    agent = TruffleAgent()
    for q in ["How do I invite team members?", "How many open tickets?"]:
        print(f"\nQ: {q}")
        r = agent.chat(q)
        print(f"A: {r['response']}")
