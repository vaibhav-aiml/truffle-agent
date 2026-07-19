"""Stateless database and Text-to-SQL execution service with connection pooling."""

import sqlite3
import contextlib
from datetime import datetime, timedelta
from pathlib import Path
from backend.utils.logger import logger

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

def convert_question_to_sql(question: str) -> dict:
    """Convert natural language questions into database SQL queries and parameters."""
    q = question.lower()
    
    # 1. Date queries
    if "today" in q or "yesterday" in q:
        if "today" in q:
            date = datetime.now().strftime("%Y-%m-%d")
            return {"sql": "SELECT * FROM tickets WHERE created_at = ?", "params": (date,), "error": None}
        elif "yesterday" in q:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            return {"sql": "SELECT * FROM tickets WHERE created_at = ?", "params": (date,), "error": None}
            
    # 2. Agent queries
    if "assigned to" in q or "by alice" in q or "by bob" in q or any(agent in q for agent in ["alice", "bob", "charlie", "diana", "eve"]):
        for agent in ["alice", "bob", "charlie", "diana", "eve"]:
            if agent in q:
                return {"sql": "SELECT * FROM tickets WHERE UPPER(assigned_to) = UPPER(?) LIMIT 20", "params": (agent,), "error": None}
                
    # 3. Time range queries
    if "last week" in q or "last month" in q:
        if "last week" in q:
            date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            return {"sql": "SELECT * FROM tickets WHERE created_at >= ?", "params": (date,), "error": None}
        elif "last month" in q:
            date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            return {"sql": "SELECT * FROM tickets WHERE created_at >= ?", "params": (date,), "error": None}

    # 4. Group by queries
    if "by status" in q or "by priority" in q or "by agent" in q:
        if "by status" in q:
            return {"sql": "SELECT status, COUNT(*) as count FROM tickets GROUP BY status", "params": (), "error": None}
        elif "by priority" in q:
            return {"sql": "SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority", "params": (), "error": None}
        elif "by agent" in q:
            return {"sql": "SELECT assigned_to, COUNT(*) as count FROM tickets GROUP BY assigned_to", "params": (), "error": None}

    # 5. Satisfaction queries
    if "satisfaction" in q or "happy" in q or "average" in q:
        if "average" in q or "satisfaction" in q:
            return {"sql": "SELECT AVG(satisfaction_score) FROM tickets WHERE satisfaction_score IS NOT NULL", "params": (), "error": None}
        elif "happy" in q:
            return {"sql": "SELECT COUNT(*) FROM tickets WHERE satisfaction_score >= ?", "params": (4,), "error": None}
        elif "unhappy" in q:
            return {"sql": "SELECT COUNT(*) FROM tickets WHERE satisfaction_score <= ?", "params": (2,), "error": None}

    # 6. Count queries
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

    # 7. List queries
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
    """Execute SQL query safely with input parameters against pooled SQLite connection."""
    if not sql:
        return {"error": "No SQL provided"}
    try:
        logger.info(f"SQL execution: {sql} | Params: {params}")
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            return {"columns": columns, "data": results, "count": len(results), "error": None}
    except Exception as e:
        logger.error(f"SQL execution failed: {e}", exc_info=True)
        return {"error": "An internal database error occurred"}

def answer_sql_question(db_path: str, question: str) -> dict:
    """Convert question to SQL, execute against database, and return formatted answer."""
    result = convert_question_to_sql(question)
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

def ensure_database_exists(db_path: str):
    """Create sqlite database structure and seed data if not found on disk."""
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
