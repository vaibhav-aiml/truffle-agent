"""Text-to-SQL converter with case-insensitive search."""

import sqlite3
import re
from pathlib import Path

class TextToSQL:
    """Convert natural language to SQL queries."""
    
    def __init__(self, db_path="data/processed/sql_db/tickets.db"):
        base_dir = Path(__file__).parent.parent.parent
        self.db_path = base_dir / db_path
    
    def convert(self, question: str) -> dict:
        """Convert natural language to SQL query."""
        q = question.lower()
        
        # Handle assigned_to queries (case-insensitive)
        if "assigned to" in q or "assigned to alice" in q or "assigned to bob" in q:
            return self._handle_assigned_to(question)
        
        # Handle COUNT queries
        if "how many" in q or "count" in q:
            return self._handle_count(q)
        
        # Handle SHOW/LIST queries
        if "show" in q or "list" in q:
            return self._handle_list(q)
        
        # Handle group by queries
        if "by status" in q or "by priority" in q or "by agent" in q:
            return self._handle_group_by(q)
        
        # Handle satisfaction queries
        if "satisfaction" in q or "average" in q:
            return self._handle_satisfaction(q)
        
        return {"sql": None, "error": "Could not understand the question"}
    
    def _handle_assigned_to(self, question):
        """Handle assigned_to queries with case-insensitive matching."""
        question_lower = question.lower()
        
        # Extract agent name
        agents = ["alice", "bob", "charlie", "diana", "eve"]
        for agent in agents:
            if agent in question_lower:
                # Use UPPER() for case-insensitive comparison
                sql = f"SELECT * FROM tickets WHERE UPPER(assigned_to) = UPPER('{agent}') LIMIT 20"
                return {"sql": sql, "error": None}
        
        return {"sql": None, "error": "Agent not found"}
    
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
        """Handle LIST/SHOW queries."""
        sql = "SELECT * FROM tickets WHERE 1=1"
        
        if "open" in question:
            sql += " AND status = 'open'"
        if "resolved" in question:
            sql += " AND status = 'resolved'"
        if "urgent" in question or "high priority" in question:
            sql += " AND priority IN ('high', 'urgent')"
        
        sql += " LIMIT 20"
        return {"sql": sql, "error": None}
    
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
        return {"sql": None, "error": "Satisfaction query not recognized"}
    
    def execute(self, sql: str) -> dict:
        """Execute SQL query and return results."""
        if not sql:
            return {"error": "No SQL provided"}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            conn.close()
            
            return {"columns": columns, "data": results, "count": len(results), "error": None}
        except Exception as e:
            return {"error": str(e)}
    
    def answer(self, question: str) -> dict:
        """Convert question to SQL, execute, return formatted answer."""
        result = self.convert(question)
        
        if result["error"]:
            return {"answer": result["error"], "sql": None, "data": None}
        
        exec_result = self.execute(result["sql"])
        
        if exec_result["error"]:
            return {"answer": f"Database error: {exec_result['error']}", "sql": result["sql"], "data": None}
        
        # Format answer based on query type
        if "COUNT" in result["sql"].upper():
            count = exec_result["data"][0][0]
            return {
                "answer": f"📊 {count} ticket(s) found.",
                "sql": result["sql"],
                "data": exec_result["data"]
            }
        elif "GROUP BY" in result["sql"].upper():
            lines = [f"  • {row[0]}: {row[1]}" for row in exec_result["data"]]
            return {
                "answer": "📈 Breakdown:\n" + "\n".join(lines),
                "sql": result["sql"],
                "data": exec_result["data"]
            }
        elif "AVG" in result["sql"].upper():
            avg = exec_result["data"][0][0]
            return {
                "answer": f"⭐ Average satisfaction score: {avg:.1f}/5.0",
                "sql": result["sql"],
                "data": exec_result["data"]
            }
        else:
            if exec_result["count"] == 0:
                return {
                    "answer": "No tickets found matching your query.",
                    "sql": result["sql"],
                    "data": []
                }
            else:
                preview = "\n".join([f"  • Ticket #{row[0]}: {row[3][:50]}..." for row in exec_result["data"][:5]])
                return {
                    "answer": f"📋 Found {exec_result['count']} ticket(s):\n{preview}",
                    "sql": result["sql"],
                    "data": exec_result["data"]
                }

if __name__ == "__main__":
    t2sql = TextToSQL()
    
    test_queries = [
        "Show tickets assigned to Bob",
        "How many open tickets?",
        "tickets by status"
    ]
    
    for q in test_queries:
        print(f"\n🔍 Q: {q}")
        result = t2sql.answer(q)
        print(f"📝 A: {result['answer']}")
        print(f"📊 SQL: {result['sql']}")
