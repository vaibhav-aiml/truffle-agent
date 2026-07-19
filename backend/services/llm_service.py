"""Stateless Groq LLM service routines."""

import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from backend.utils.logger import logger

def create_groq_client(api_key: str = None, model: str = None) -> ChatGroq | None:
    """Factory function to build a ChatGroq instance, handling key lookups and fallback checks."""
    api_key = api_key or os.environ.get("GROQ_API_KEY")
    model = model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.environ.get("GROQ_API_KEY")
        
    if not api_key:
        logger.warning("GROQ_API_KEY not found in environment. Truffle will run in LOCAL RAG fallback mode.")
        return None
        
    logger.info(f"Initializing Groq client with model: {model}")
    try:
        client = ChatGroq(
            model=model,
            api_key=api_key,
            temperature=0.1,
            max_tokens=2000,
            max_retries=2
        )
        logger.info("Groq client created successfully.")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize ChatGroq client: {e}", exc_info=True)
        return None

def answer_with_context(client: ChatGroq | None, query: str, context: str) -> str:
    """Answer support queries using the provided text context and Groq model."""
    if not client:
        # Fallback RAG representation
        return f"Based on our knowledge base:\n\n{context}\n\n*(Note: Running in offline fallback mode)*"
        
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
    
    try:
        response = client.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        logger.error(f"Error invoking Groq LLM: {e}", exc_info=True)
        return f"Based on our knowledge base:\n\n{context}\n\n*(Note: LLM request failed. Returned local match context)*"

def answer_with_custom_prompt(client: ChatGroq | None, prompt: str) -> str:
    """Answer with custom prompt."""
    if not client:
        return "Local fallback: LLM query options are disabled when GROQ_API_KEY is not set."
    try:
        response = client.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        logger.error(f"Error invoking Groq with custom prompt: {e}", exc_info=True)
        return "Failed to run custom LLM prompt."
