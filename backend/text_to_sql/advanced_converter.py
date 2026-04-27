"""Advanced Text-to-SQL converter with complex query support."""

import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path

class AdvancedTextToSQL:
    """Convert natural language to complex SQL queries."""
    
    def __init__(self, db_path="data/processed/sql_db/tickets.db"):
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database exists with sample data."""
        db_file = Path(self.db_path)
        if not db_file.exists():
            print("📊 Creating database with sample data...")
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Create richer sample data for complex queries."""
        import random
        
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS tickets")
        cursor.execute("""
        CREATE TABLE tickets (
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
        
        # Sample data with dates, agents, categories
        customers = [
            ("John Smith", "john@example.com"),
            ("Sarah Johnson", "sarah@example.com"),
            ("Mike Brown", "mike@example.com"),
            ("Lisa Wilson", "lisa@example.com"),
            ("David Lee", "david@example.com"),
        ]
        
        agents = ["Alice", "Bob", "Charlie", "Diana"]
        statuses = ["open", "in_progress", "resolved", "closed"]
        priorities = ["low", "medium", "high", "urgent"]
        categories = ["technical", "billing", "account", "feature_request", "bug"]
        
        tickets = []
        for i in range(1, 101):
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
        
        cursor.executemany("""
        INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, tickets)
        
        conn.commit()
        conn.close()
        print(f"✅ Created {len(tickets)} tickets with dates and agents")
    
    def convert(self, question: str) -> dict:
        """Convert natural language to SQL with advanced patterns."""
        q = question.lower()
        
        # Date-based queries
        if "today" in q or "yesterday" in q:
            return self._handle_date_query(q)
        
        # Agent-based queries
        if "assigned to" in q or "by alice" in q or "by bob" in q:
            return self._handle_agent_query(q)
        
        # Time range queries
        if "last week" in q or "last month" in q:
            return self._handle_time_range(q)
        
        # Group by queries
        if "by status" in q or "by priority" in q or "by agent" in q:
            return self._handle_group_by(q)
        
        # Satisfaction queries
        if "satisfaction" in q or "happy" in q:
            return self._handle_satisfaction(q)
        
        # Default handlers
        if "how many" in q or "count" in q:
            return self._handle_count(q)
        
        if "show" in q or "list" in q:
            return self._handle_list(q)
        
        return {"sql": None, "error": "Could not understand. Try: 'tickets created today', 'tickets by status', 'assigned to Alice'"}
    
    def _handle_date_query(self, question):
        """Handle date-based queries."""
        if "today" in question:
            date = datetime.now().strftime("%Y-%m-%d")
            return {"sql": f"SELECT * FROM tickets WHERE created_at = '{date}'", "error": None}
        elif "yesterday" in question:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            return {"sql": f"SELECT * FROM tickets WHERE created_at = '{date}'", "error": None}
        return {"sql": None, "error": "Date query not recognized"}
    
    def _handle_agent_query(self, question):
        """Handle agent assignment queries."""
        for agent in ["alice", "bob", "charlie", "diana"]:
            if agent in question:
                return {"sql": f"SELECT * FROM tickets WHERE LOWER(assigned_to) = '{agent}'", "error": None}
        return {"sql": None, "error": "Agent not found"}
    
    def _handle_time_range(self, question):
        """Handle time range queries."""
        if "last week" in question:
            date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            return {"sql": f"SELECT * FROM tickets WHERE created_at >= '{date}'", "error": None}
        elif "last month" in question:
            date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            return {"sql": f"SELECT * FROM tickets WHERE created_at >= '{date}'", "error": None}
        return {"sql": None, "error": "Time range not recognized"}
    
    def _handle_group_by(self, question):
        """Handle GROUP BY queries."""
        if "by status" in question:
            return {"sql": "SELECT status, COUNT(*) as count FROM tickets GROUP BY status", "error": None}
        elif "by priority" in question:
            return {"sql": "SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority", "error": None}
        elif "by agent" in question:
            return {"sql": "SELECT assigned_to, COUNT(*) as count FROM tickets GROUP BY assigned_to", "error": None}
        return {"sql": None, "error": "Group by not recognized"}
    
    def _handle_satisfaction(self, question):
        """Handle satisfaction queries."""
        if "average" in question:
            return {"sql": "SELECT AVG(satisfaction_score) FROM tickets WHERE satisfaction_score IS NOT NULL", "error": None}
        elif "happy" in question:
            return {"sql": "SELECT COUNT(*) FROM tickets WHERE satisfaction_score >= 4", "error": None}
        elif "unhappy" in question:
            return {"sql": "SELECT COUNT(*) FROM tickets WHERE satisfaction_score <= 2", "error": None}
        return {"sql": None, "error": "Satisfaction query not recognized"}
    
    def _handle_count(self, question):
        """Handle COUNT queries."""
        sql = "SELECT COUNT(*) FROM tickets"
        
        if "open" in question:
            sql += " WHERE status = 'open'"
        elif "resolved" in question:
            sql += " WHERE status = 'resolved'"
        elif "closed" in question:
            sql += " WHERE status = 'closed'"
        elif "urgent" in question or "high priority" in question:
            sql += " WHERE priority IN ('high', 'urgent')"
        
        return {"sql": sql, "error": None}
    
    def _handle_list(self, question):
        """Handle LIST queries."""
        sql = "SELECT * FROM tickets WHERE 1=1"
        
        if "open" in question:
            sql += " AND status = 'open'"
        if "urgent" in question or "high priority" in question:
            sql += " AND priority IN ('high', 'urgent')"
        
        sql += " LIMIT 20"
        return {"sql": sql, "error": None}
    
    def execute(self, sql: str) -> dict:
        """Execute SQL and return results."""
        if not sql:
            return {"error": "No SQL provided"}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.counter()
            cursor.execute(sql)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            conn.close()
            
            return {"columns": columns, "data": results, "count": len(results), "error": None}
        except Exception as e:
            return {"error": str(e)}
    
    def format_answer(self, question: str) -> dict:
        """Convert, execute, and format answer."""
        result = self.convert(question)
        
        if result["error"]:
            return {"answer": result["error"], "sql": None}
        
        exec_result = self.execute(result["sql"])
        
        if exec_result["error"]:
            return {"answer": f"Error: {exec_result['error']}", "sql": result["sql"]}
        
        # Format based on query type
        if "COUNT" in result["sql"].upper():
            count = exec_result["data"][0][0]
            return {"answer": f"📊 {count} ticket(s) found", "sql": result["sql"], "data": exec_result["data"]}
        elif "AVG" in result["sql"].upper():
            avg = exec_result["data"][0][0]
            return {"answer": f"⭐ Average satisfaction: {avg:.1f}/5.0", "sql": result["sql"], "data": exec_result["data"]}
        elif "GROUP BY" in result["sql"].upper():
            lines = [f"  • {row[0]}: {row[1]}" for row in exec_result["data"]]
            return {"answer": "📈 Breakdown:\n" + "\n".join(lines), "sql": result["sql"], "data": exec_result["data"]}
        else:
            if exec_result["count"] == 0:
                return {"answer": "No tickets found", "sql": result["sql"], "data": []}
            else:
                preview = "\n".join([f"  • Ticket #{row[0]}: {row[3][:50]}..." for row in exec_result["data"][:5]])
                return {"answer": f"📋 Found {exec_result['count']} tickets:\n{preview}", "sql": result["sql"], "data": exec_result["data"]}

if __name__ == "__main__":
    t2sql = AdvancedTextToSQL()
    
    test_queries = [
        "How many open tickets?",
        "tickets by status",
        "assigned to Alice",
        "tickets created last week",
        "average satisfaction score"
    ]
    
    for q in test_queries:
        print(f"\n🔍 Q: {q}")
        result = t2sql.format_answer(q)
        print(f"📝 A: {result['answer']}")
        print(f"📊 SQL: {result['sql']}")
