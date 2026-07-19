"""Stateless functional agent routing orchestrator."""

from backend.config import settings
from backend.services.sql_service import answer_sql_question
from backend.services.vector_service import load_vector_db, create_openai_client, search_vector_db
from backend.services.llm_service import create_groq_client, answer_with_context
from backend.utils.logger import logger

def create_agent_context(db_path: str = None, storage_path: str = None) -> dict:
    """Build and load the database, vector DB, and client states for routing."""
    db_path = db_path or str(settings.DB_PATH)
    storage_path = storage_path or str(settings.VECTOR_DB_DIR)
    
    logger.info(f"Initializing functional agent context (DB={db_path}, Storage={storage_path})")
    
    return {
        "db_path": db_path,
        "storage_path": storage_path,
        "documents": load_vector_db(storage_path),
        "groq_client": create_groq_client(),
        "openai_client": create_openai_client()
    }

def get_rag_answer(context: dict, query: str) -> dict:
    """Find matches in the vector database and generate answer via Groq LLM."""
    documents = context.get("documents", [])
    openai_client = context.get("openai_client")
    groq_client = context.get("groq_client")
    
    try:
        # Search the vector database using stateless function
        results = search_vector_db(openai_client, documents, query, top_k=2)
        
        if results and results[0]["similarity"] > 0.30:
            best_match = results[0]
            logger.info(f"RAG hit: source={best_match['metadata'].get('source')} | similarity={best_match['similarity']:.3f}")
            
            combined_context = "\n\n".join([r["content"] for r in results])
            sources = list(set([r["metadata"].get("source", "unknown") for r in results]))
            
            response = answer_with_context(groq_client, query, combined_context)
            
            confidence = int(best_match["similarity"] * 100)
            confidence = min(99, max(50, confidence))
            
            return {
                "response": response,
                "confidence": confidence,
                "type": "rag",
                "sources": sources
            }
    except Exception as e:
        logger.error(f"Functional RAG routing error: {e}", exc_info=True)
        
    logger.info("RAG search missed: using default policy instruction responses.")
    return {
        "response": "I couldn't find a direct answer in our documentation. Try asking about: team invites, cancellation steps, mobile app features, password resets, pricing subscription plans, or refund policies.",
        "confidence": 50,
        "type": "rag",
        "sources": ["Default System Route"]
    }

def chat_with_agent(context: dict, query: str) -> dict:
    """Route queries dynamically to Text-to-SQL or Document RAG handlers."""
    query_lower = query.lower()
    db_path = context.get("db_path")
    
    db_keywords = ["ticket", "tickets", "open", "resolved", "priority", 
                   "assigned to", "satisfaction", "count tickets", "how many",
                   "show me", "list tickets", "tickets by", "group by", "average satisfaction"]
                   
    is_db_query = any(keyword in query_lower for keyword in db_keywords)
    
    if is_db_query:
        logger.info(f"Routing query to SQL service: {query}")
        try:
            result = answer_sql_question(db_path, query)
            
            # Check for SQL error cases
            if not result.get("sql") and "error" in result.get("answer", "").lower():
                return {
                    "query": query,
                    "response": result["answer"],
                    "confidence": 50,
                    "type": "error",
                    "sources": []
                }
                
            return {
                "query": query,
                "response": result["answer"],
                "confidence": 94,
                "type": "sql",
                "sql": result.get("sql"),
                "sources": ["Database Query"],
                "documents_used": 0
            }
        except Exception as e:
            logger.error(f"SQL service router failed: {e}", exc_info=True)
            return {
                "query": query,
                "response": "An error occurred while compiling your database query. Please try again.",
                "confidence": 50,
                "type": "error",
                "sources": []
            }
    else:
        logger.info(f"Routing query to RAG service: {query}")
        rag_result = get_rag_answer(context, query)
        return {
            "query": query,
            "response": rag_result["response"],
            "confidence": rag_result["confidence"],
            "type": rag_result["type"],
            "sources": rag_result["sources"]
        }
