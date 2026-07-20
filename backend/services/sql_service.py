"""Stateless database and Text-to-SQL execution service with connection pooling.

All queries executed through execute_sql_query are protected by a SQLite
connection-level authorizer that only permits read operations (SELECT, READ,
FUNCTION, TRANSACTION). This provides defense-in-depth against both
LLM-generated and heuristic query paths.
"""

import sqlite3
import contextlib
from datetime import datetime, timedelta
from pathlib import Path
from backend.utils.logger import logger

# ---------------------------------------------------------------------------
# SQLite read-only authorizer
# ---------------------------------------------------------------------------
# Explicit allowlist of action codes that are safe for read-only queries.
# Everything else is denied at the connection level, preventing write
# operations even if they bypass string-level validation.
_ALLOWED_ACTIONS: frozenset[int] = frozenset({
    sqlite3.SQLITE_SELECT,       # 21 — SELECT statement
    sqlite3.SQLITE_READ,         # 20 — reading a column value
    sqlite3.SQLITE_FUNCTION,     # 31 — calling a function (COUNT, AVG, etc.)
    sqlite3.SQLITE_TRANSACTION,  # 22 — BEGIN / COMMIT / ROLLBACK (read txn)
})


def _read_only_authorizer(action: int, arg1, arg2, db_name, trigger_name) -> int:
    """SQLite authorizer callback that denies all non-read operations.

    Blocks INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, PRAGMA, ATTACH,
    DETACH, and all other mutation action codes. Only SQLITE_SELECT,
    SQLITE_READ, SQLITE_FUNCTION, and SQLITE_TRANSACTION are allowed.
    """
    if action in _ALLOWED_ACTIONS:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


@contextlib.contextmanager
def get_db_connection(db_path: str):
    """Obtain a SQLite database connection with concurrent WAL journaling and high timeout thresholds."""
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
        # Enable Write-Ahead Logging (WAL) for safe concurrent reads/writes
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        yield conn
    except Exception as e:
        logger.error(f"SQLite pool connection failed for {db_path}: {e}", exc_info=True)
        raise
    finally:
        if conn:
            conn.close()


@contextlib.contextmanager
def _get_readonly_connection(db_path: str):
    """Obtain a read-only SQLite connection with the authorizer enforced."""
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.set_authorizer(_read_only_authorizer)
        yield conn
    except Exception as e:
        logger.error(f"SQLite read-only connection failed for {db_path}: {e}", exc_info=True)
        raise
    finally:
        if conn:
            conn.close()


def convert_question_to_sql(question: str, groq_client=None) -> dict:
    """Convert natural language questions into database SQL queries and parameters."""
    q = question.lower()
    
    # 1. Attempt LLM-based SQL translation if client is available
    if groq_client:
        from langchain_core.messages import HumanMessage
        schema_info = (
            "Table schema:\n"
            "tickets (\n"
            "    id INTEGER PRIMARY KEY,\n"
            "    customer_name TEXT,\n"
            "    customer_email TEXT,\n"
            "    subject TEXT,\n"
            "    description TEXT,\n"
            "    status TEXT,\n"
            "    priority TEXT,\n"
            "    assigned_to TEXT,\n"
            "    created_at DATE,\n"
            "    resolved_at DATE,\n"
            "    satisfaction_score INTEGER,\n"
            "    category TEXT\n"
            ")"
        )
        prompt = f"""You are a SQLite expert. Convert this natural language question into a read-only SELECT query.
        
{schema_info}

Rules:
1. Return ONLY the raw SQL query. Do NOT wrap it in markdown blocks, backticks, or any explanation.
2. The query MUST be a SELECT statement. Do NOT allow modification commands (INSERT, UPDATE, DELETE, DROP, ALTER).
3. Limit the results to a maximum of 20 unless a specific count or limit is requested.
4. Try to make it simple and safe.

Question: {question}
SQL:"""
        try:
            logger.info("Attempting LLM-based Text-to-SQL translation.")
            response = groq_client.invoke([HumanMessage(content=prompt)])
            sql_candidate = response.content.strip().replace("```sql", "").replace("```", "").strip()
            
            # String-level pre-check (belt-and-suspenders with the authorizer)
            sql_lower = sql_candidate.lower()
            if (sql_lower.startswith("select") and 
                not any(cmd in sql_lower for cmd in [
                    "insert", "update", "delete", "drop", "alter",
                    "create", "pragma", "attach", "detach"
                ])):
                logger.info(f"LLM-generated SQL query: {sql_candidate}")
                return {"sql": sql_candidate, "params": (), "error": None}
            else:
                logger.warning(f"LLM-generated SQL query was rejected for safety: {sql_candidate}")
        except Exception as e:
            logger.error(f"LLM-based Text-to-SQL translation failed: {e}", exc_info=True)
            
    # 2. Fallback heuristic queries
    # Date queries
    if "today" in q or "yesterday" in q:
        if "today" in q:
            date = datetime.now().strftime("%Y-%m-%d")
            return {"sql": "SELECT * FROM tickets WHERE created_at = ?", "params": (date,), "error": None}
        elif "yesterday" in q:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            return {"sql": "SELECT * FROM tickets WHERE created_at = ?", "params": (date,), "error": None}
            
    # Agent queries
    if "assigned to" in q or "by alice" in q or "by bob" in q or any(agent in q for agent in ["alice", "bob", "charlie", "diana", "eve"]):
        for agent in ["alice", "bob", "charlie", "diana", "eve"]:
            if agent in q:
                return {"sql": "SELECT * FROM tickets WHERE UPPER(assigned_to) = UPPER(?) LIMIT 20", "params": (agent,), "error": None}
                
    # Time range queries
    if "last week" in q or "last month" in q:
        if "last week" in q:
            date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            return {"sql": "SELECT * FROM tickets WHERE created_at >= ?", "params": (date,), "error": None}
        elif "last month" in q:
            date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            return {"sql": "SELECT * FROM tickets WHERE created_at >= ?", "params": (date,), "error": None}
 
    # Group by queries
    if "by status" in q or "by priority" in q or "by agent" in q:
        if "by status" in q:
            return {"sql": "SELECT status, COUNT(*) as count FROM tickets GROUP BY status", "params": (), "error": None}
        elif "by priority" in q:
            return {"sql": "SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority", "params": (), "error": None}
        elif "by agent" in q:
            return {"sql": "SELECT assigned_to, COUNT(*) as count FROM tickets GROUP BY assigned_to", "params": (), "error": None}
 
    # Satisfaction queries
    if "satisfaction" in q or "happy" in q or "average" in q:
        if "average" in q or "satisfaction" in q:
            return {"sql": "SELECT AVG(satisfaction_score) FROM tickets WHERE satisfaction_score IS NOT NULL", "params": (), "error": None}
        elif "happy" in q:
            return {"sql": "SELECT COUNT(*) FROM tickets WHERE satisfaction_score >= ?", "params": (4,), "error": None}
        elif "unhappy" in q:
            return {"sql": "SELECT COUNT(*) FROM tickets WHERE satisfaction_score <= ?", "params": (2,), "error": None}
 
    # Count queries
    if "how many" in q or "count" in q:
        sql = "SELECT COUNT(*) FROM tickets"
        params = []
        if "open" in q:
            sql += " WHERE status = ?"
            params.append("open")
        elif "resolved" in q:
            sql += " WHERE status = ?"
            params.append("resolved")
        elif "closed" in q:
            sql += " WHERE status = ?"
            params.append("closed")
        elif "urgent" in q or "high priority" in q:
            sql += " WHERE priority IN (?, ?)"
            params.extend(["high", "urgent"])
        return {"sql": sql, "params": tuple(params), "error": None}
 
    # List queries
    if "show" in q or "list" in q:
        sql = "SELECT * FROM tickets WHERE 1=1"
        params = []
        if "open" in q:
            sql += " AND status = ?"
            params.append("open")
        if "resolved" in q:
            sql += " AND status = ?"
            params.append("resolved")
        if "urgent" in q or "high priority" in q:
            sql += " AND priority IN (?, ?)"
            params.extend(["high", "urgent"])
        sql += " LIMIT 20"
        return {"sql": sql, "params": tuple(params), "error": None}
 
    return {"sql": None, "params": (), "error": "Could not understand the question"}
 
def execute_sql_query(db_path: str, sql: str, params: tuple = ()) -> dict:
    """Execute SQL query with read-only authorizer enforcement.

    All queries — whether LLM-generated or heuristic — pass through a
    connection with set_authorizer enforcing a strict read-only allowlist.
    """
    if not sql:
        return {"error": "No SQL provided"}
    try:
        logger.info(f"SQL execution: {sql} | Params: {params}")
        with _get_readonly_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            return {"columns": columns, "data": results, "count": len(results), "error": None}
    except sqlite3.DatabaseError as e:
        logger.error(f"SQL execution blocked or failed: {e}", exc_info=True)
        return {"error": "Query blocked by read-only enforcement policy"}
    except Exception as e:
        logger.error(f"SQL execution failed: {e}", exc_info=True)
        return {"error": "An internal database error occurred"}
 
def answer_sql_question(db_path: str, question: str, groq_client=None) -> dict:
    """Convert question to SQL, execute against database, and return formatted answer."""
    result = convert_question_to_sql(question, groq_client)
    if result["error"]:
        return {"answer": result["error"], "sql": None, "data": None}
        
    exec_result = execute_sql_query(db_path, result["sql"], result["params"])
    if exec_result["error"]:
        return {"answer": f"Database error: {exec_result['error']}", "sql": result["sql"], "data": None}
        
    # Format answer based on query type
    sql_upper = result["sql"].upper()
    if "COUNT" in sql_upper:
        count = exec_result["data"][0][0]
        return {"answer": f"📊 {count} ticket(s) found.", "sql": result["sql"], "data": exec_result["data"]}
    elif "GROUP BY" in sql_upper:
        lines = [f"  • {row[0]}: {row[1]}" for row in exec_result["data"]]
        return {"answer": "📈 Breakdown:\n" + "\n".join(lines), "sql": result["sql"], "data": exec_result["data"]}
    elif "AVG" in sql_upper:
        avg = exec_result["data"][0][0] or 0.0
        return {"answer": f"⭐ Average satisfaction score: {avg:.1f}/5.0", "sql": result["sql"], "data": exec_result["data"]}
    else:
        if exec_result["count"] == 0:
            return {"answer": "No tickets found matching your query.", "sql": result["sql"], "data": []}
        else:
            preview = "\n".join([f"  • Ticket #{row[0]}: {row[3][:50]}..." for row in exec_result["data"][:5]])
            return {"answer": f"📋 Found {exec_result['count']} ticket(s):\n{preview}", "sql": result["sql"], "data": exec_result["data"]}

def ensure_database_exists(db_path: str) -> None:
    """Create sqlite database structure, seed data, and add indexes if not found on disk."""
    db_file = Path(db_path)
    if db_file.exists():
        return
    db_file.parent.mkdir(parents=True, exist_ok=True)
    import random
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY,
            customer_name TEXT,
            customer_email TEXT,
            subject TEXT,
            description TEXT,
            status TEXT,
            priority TEXT,
            assigned_to TEXT,
            created_at DATE,
            resolved_at DATE,
            satisfaction_score INTEGER,
            category TEXT
        )
        """)
        
        # Create indexes on high-cardinality filter columns used by most queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at)")
        
        customers = [
            ("John Smith", "john@example.com"),
            ("Sarah Johnson", "sarah@example.com"),
            ("Mike Brown", "mike@example.com"),
            ("Lisa Wilson", "lisa@example.com"),
            ("David Lee", "david@example.com"),
            ("Anna Martinez", "anna@example.com"),
            ("James Taylor", "james@example.com"),
        ]
        agents = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        statuses = ["open", "in_progress", "resolved", "closed"]
        priorities = ["low", "medium", "high", "urgent"]
        categories = ["technical", "billing", "account", "feature_request", "bug"]
        
        tickets = []
        for i in range(1, 51):
            customer = random.choice(customers)
            created_date = datetime.now() - timedelta(days=random.randint(0, 60))
            status = random.choice(statuses)
            priority = random.choice(priorities)
            
            resolved_date = None
            satisfaction = None
            
            if status in ["resolved", "closed"]:
                resolved_date = created_date + timedelta(days=random.randint(1, 10))
                satisfaction = random.randint(1, 5)
                
            tickets.append((
                i, customer[0], customer[1],
                f"Ticket #{i}: {random.choice(categories)} issue",
                f"Description for ticket {i}",
                status, priority, random.choice(agents),
                created_date.strftime("%Y-%m-%d"),
                resolved_date.strftime("%Y-%m-%d") if resolved_date else None,
                satisfaction, random.choice(categories)
            ))
            
        cursor.executemany("INSERT OR REPLACE INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", tickets)
        conn.commit()
    logger.info(f"Database initialized with {len(tickets)} tickets at {db_path}.")
