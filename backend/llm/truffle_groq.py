"""Truffle AI with Free Groq API - Complete Answers."""

import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

class TruffleGroq:
    """Truffle using free Groq API with complete answers."""
    
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not self.api_key:
            from dotenv import load_dotenv
            load_dotenv()
            self.api_key = os.environ.get("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        print(f"🍄 Initializing Groq with model: {self.model}")
        
        self.llm = ChatGroq(
            model=self.model,
            api_key=self.api_key,
            temperature=0.1,
            max_tokens=2000,  # Increased for complete answers
            max_retries=2
        )
        print(f"✅ Truffle Groq ready!")
    
    def answer_with_context(self, query: str, context: str) -> str:
        """Answer question using retrieved context with complete response."""
        prompt = f"""You are Truffle, an AI support agent. Answer the question based ONLY on the context below.

CONTEXT:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Answer ONLY using information from the context above
2. Provide COMPLETE, DETAILED answers
3. Use bullet points or numbered lists for multiple items
4. Don't cut off answers - provide all information
5. Be helpful and professional

ANSWER:"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    def answer_with_custom_prompt(self, prompt: str) -> str:
        """Answer with custom prompt."""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

if __name__ == "__main__":
    truffle = TruffleGroq()
    result = truffle.answer_with_context(
        "What payment methods do you accept?",
        "We accept Visa, Mastercard, American Express, Discover, PayPal, Apple Pay, Google Pay, and Bank Transfer for Enterprise plans."
    )
    print(f"Test: {result}")
