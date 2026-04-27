"""Main Truffle agent orchestration."""

from backend.rag.retriever import Retriever, setup_knowledge_base
from backend.evaluation.test_cases import get_all_test_cases

class SupportAgent:
    """Orchestrates all Truffle components."""
    
    def __init__(self):
        print("🍄 Initializing Truffle Agent...")
        self.retriever = setup_knowledge_base()
        print("✅ Truffle Agent ready!")
    
    def answer_query(self, query: str) -> dict:
        """Process a user query and return response."""
        # Get relevant documents
        context = self.retriever.retrieve_with_context(query)
        
        # Simple response (upgrade later with LLM)
        if context["documents"]:
            best_doc = context["documents"][0]
            response = f"Based on our knowledge base: {best_doc['content'][:200]}..."
            confidence = best_doc["similarity"]
        else:
            response = "I couldn't find an answer. Please contact support."
            confidence = 0.0
        
        return {
            "query": query,
            "response": response,
            "confidence": confidence,
            "sources": context["sources"],
            "documents_used": len(context["documents"])
        }
    
    def evaluate(self) -> dict:
        """Run evaluation on test cases."""
        test_cases = get_all_test_cases()
        results = []
        
        for test in test_cases:
            result = self.answer_query(test["query"])
            results.append({
                "query": test["query"],
                "expected": test.get("expected_answer_contains", []),
                "response": result["response"],
                "confidence": result["confidence"]
            })
        
        return {
            "total": len(results),
            "results": results
        }

if __name__ == "__main__":
    agent = SupportAgent()
    
    # Test queries
    test_queries = [
        "How do I reset my password?",
        "What subscription plans do you have?",
        "How do I get a refund?"
    ]
    
    print("\n📝 Testing agent:")
    for query in test_queries:
        result = agent.answer_query(query)
        print(f"\n🔍 Q: {query}")
        print(f"💬 A: {result['response'][:100]}...")
        print(f"📊 Confidence: {result['confidence']:.2f}")
