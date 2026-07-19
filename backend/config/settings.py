"""Configuration settings and constant path definitions for Truffle."""

import os
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).parent.parent.parent

# Database settings
DB_PATH = BASE_DIR / os.environ.get("TRUFFLE_DB_PATH", "data/processed/sql_db/tickets.db")

# Vector storage settings
VECTOR_DB_DIR = BASE_DIR / os.environ.get("TRUFFLE_VECTOR_DIR", "data/processed/embeddings")

# Logging settings
LOG_FILE = BASE_DIR / os.environ.get("TRUFFLE_LOG_FILE", "data/truffle.log")

# Redis configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Sentry DSN configuration
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

# Rate Limit settings
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))       # in seconds
RATE_LIMIT_MAX_REQUESTS = int(os.environ.get("RATE_LIMIT_MAX_REQUESTS", "30")) # max requests per window

# Cache settings
CACHE_TTL = int(os.environ.get("CACHE_TTL", "86400")) # TTL in seconds (24 hours default)

# Ensure required folders exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
