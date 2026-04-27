"""Text-to-SQL converter for Truffle."""

import sqlite3
import re
from pathlib import Path

class TextToSQL:
    """Convert natural language to SQL queries."""
    
    def __init__(self, db_path="data/processed/sql_db/tickets.db"):
        self.db_path = db_path
        self.schema = self._get_schema()
    
    def _get_schema(self):
        """Get database schema."""
        return """
        tickets table schema:
        - id (INTEGER): Ticket ID
        - customer_name (TEXT): Customer full name
        - customer_email (TEXT): Customer email address
        - subject (TEXT): Ticket subject line
        - description (TEXT): Ticket description
        - status (TEXT): Values: open, in_progress, resolved, closed
        - priority (TEXT): Values: low, medium, high, urgent
        - assigned_to (TEXT): Agent name
        - created_at (DATE): When ticket was created
        - resolved_at (DATE): When ticket was resolved (NULL if not resolved)
        - satisfaction_score (INTEGER): 1-5, NULL if not resolved
        """
    
    def convert(self, question: str) -> dict:
        """Convert natural language to SQL query."""
        question_lower = question.lower()
        
        # COUNT queries
        if "how many" in question_lower or "count" in question_lower:
            return self._handle_count(question_lower)
        
        # SHOW/LIST queries
        if any(word in question_lower for word in ["show", "list", "get", "find"]):
            return self._handle_list(question_lower)
        
        # AVERAGE queries
        if "average" in question_lower:
            return self._handle_average(question_lower)
        
        # Default
        return {
            "sql": None,
            "error": "Could not understand the question. Try: 'How many open tickets?', 'Show high priority tickets'"
        }
    
    def _handle_count(self, question):
        """Handle COUNT queries."""
        sql = "SELECT COUNT(*) FROM tickets"
        
        if "open" in question:
            sql += " WHERE status = 'open'"
        elif "resolved" in question:
            sql += " WHERE status = 'resolved'"
        elif "closed" in question:
            sql += " WHERE status = 'closed'"
        elif "high priority" in question or "urgent" in question:
            sql += " WHERE priority IN ('high', 'urgent')"
        
        return {"sql": sql, "error": None}
    
    def _handle_list(self, question):
        """Handle LIST/SHOW queries."""
        sql = "SELECT * FROM tickets"
        conditions = []
        
        if "open" in question:
            conditions.append("status = 'open'")
        elif "resolved" in question:
            conditions.append("status = 'resolved'")
        
        if "high priority" in question or "urgent" in question:
            conditions.append("priority IN ('high', 'urgent')")
        
        if "assigned to" in question:
            import re
            match = re.search(r'assigned to (\w+)', question)
            if match:
                conditions.append(f"assigned_to = '{match.group(1)}'")
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " LIMIT 20"
        
        return {"sql": sql, "error": None}
    
    def _handle_average(self, question):
        """Handle AVERAGE queries."""
        sql = "SELECT AVG(satisfaction_score) FROM tickets"
        
        if "resolved" in question:
            sql += " WHERE satisfaction_score IS NOT NULL"
        
        return {"sql": sql, "error": None}
    
    def execute(self, sql: str) -> dict:
        """Execute SQL query and return results."""
        if not sql:
            return {"error": "No SQL query provided"}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql)
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Fetch results
            results = cursor.fetchall()
            conn.close()
            
            return {
                "columns": columns,
                "data": results,
                "count": len(results),
                "error": None
            }
        except Exception as e:
            return {"error": str(e), "data": None}
    
    def answer(self, question: str) -> dict:
        """Convert question to SQL, execute, return formatted answer."""
        # Convert to SQL
        result = self.convert(question)
        
        if result["error"]:
            return {"answer": result["error"], "sql": None, "data": None}
        
        # Execute SQL
        exec_result = self.execute(result["sql"])
        
        if exec_result["error"]:
            return {"answer": f"Database error: {exec_result['error']}", "sql": result["sql"], "data": None}
        
        # Format answer
        if "COUNT" in result["sql"].upper():
            count = exec_result["data"][0][0]
            return {
                "answer": f"📊 {count} ticket(s) found.",
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
            count = exec_result["count"]
            if count == 0:
                return {
                    "answer": "No tickets found matching your query.",
                    "sql": result["sql"],
                    "data": []
                }
            else:
                preview = "\n".join([f"  • Ticket #{row[0]}: {row[3][:50]}..." for row in exec_result["data"][:5]])
                return {
                    "answer": f"📋 Found {count} ticket(s):\n{preview}",
                    "sql": result["sql"],
                    "data": exec_result["data"]
                }

if __name__ == "__main__":
    t2sql = TextToSQL()
    
    test_questions = [
        "How many open tickets?",
        "Show me high priority tickets",
        "How many resolved tickets?",
        "Average satisfaction score?"
    ]
    
    for q in test_questions:
        print(f"\n🔍 Q: {q}")
        result = t2sql.answer(q)
        print(f"📝 A: {result['answer']}")
        print(f"📊 SQL: {result['sql']}")
