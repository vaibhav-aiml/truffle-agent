"""Functional environment configuration validator module."""

import os
from pathlib import Path
from backend.config import settings
from backend.utils.logger import logger

def validate_environment() -> tuple[bool, list[str], list[str]]:
    """Validate environment variables and folder dependencies.
    
    Returns:
        (is_valid, warnings, errors)
    """
    warnings = []
    errors = []
    
    # 1. API Keys Validation
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        warnings.append("GROQ_API_KEY is missing. Truffle will run in LOCAL RAG fallback mode.")
        
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        warnings.append("OPENAI_API_KEY is missing. Local deterministic hash embeddings will be used.")
        
    # 2. Database File Verification
    db_path = settings.DB_PATH
    if not db_path.exists():
        errors.append(f"SQLite Database not found at: {db_path}. Run 'python setup_database.py' first.")
        
    # 3. Vector Embeddings DB Verification
    vector_dir = settings.VECTOR_DB_DIR
    vector_file = vector_dir / "vectors.json"
    if not vector_file.exists():
        warnings.append(f"Vector database vectors.json not found at {vector_dir}. Run 'python setup_kb.py' to seed.")
        
    # 4. Redis connection validation warning (optional)
    redis_url = settings.REDIS_URL
    if not redis_url:
        warnings.append("REDIS_URL is not set. Caching and rate limiting will fall back to in-memory dictionaries.")
        
    is_valid = len(errors) == 0
    
    # Log findings
    if errors:
        for err in errors:
            logger.error(f"[CONFIG ERROR] {err}")
    if warnings:
        for warn in warnings:
            logger.warning(f"[CONFIG WARNING] {warn}")
            
    return is_valid, warnings, errors
