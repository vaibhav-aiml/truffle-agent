"""Workflow agent with correct database path for cloud deployment."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class WorkflowAgent:
    """Automated workflow agent for ticket management."""
    
    def __init__(self, db_path="data/processed/sql_db/tickets.db"):
        # Get the correct path for cloud deployment
        base_dir = Path(__file__).parent.parent.parent
        self.db_path = base_dir / db_path
        self.actions_log = []
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database if it doesn't exist
        if not self.db_path.exists():
            self._create_database()
    
    def _create_database(self):
        """Create database with sample data if it doesn't exist."""
        import random
        from datetime import timedelta
        
        conn = sqlite3.connect(self.db_path)
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
        
        # Sample data
        customers = [
            ("John Smith", "john@example.com"),
            ("Sarah Johnson", "sarah@example.com"),
            ("Mike Brown", "mike@example.com"),
        ]
        agents = ["Alice", "Bob", "Charlie", "Diana"]
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
        
        cursor.executemany("""
        INSERT OR REPLACE INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, tickets)
        
        conn.commit()
        conn.close()
        print(f"✅ Created database with {len(tickets)} tickets")
    
    def auto_resolve_password_tickets(self) -> Dict:
        """Auto-resolve password reset tickets."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, subject, customer_email 
            FROM tickets 
            WHERE status = 'open' 
            AND (subject LIKE '%password%' OR subject LIKE '%login%')
        """)
        
        tickets = cursor.fetchall()
        resolved_count = 0
        
        for ticket in tickets:
            cursor.execute("""
                UPDATE tickets 
                SET status = 'resolved', 
                    resolved_at = ?,
                    description = description || '\n\nAuto-resolved by Truffle Agent'
                WHERE id = ?
            """, (datetime.now().strftime("%Y-%m-%d"), ticket[0]))
            
            resolved_count += 1
            self.actions_log.append({
                "action": "auto_resolve",
                "ticket_id": ticket[0],
                "reason": "Password reset request"
            })
        
        conn.commit()
        conn.close()
        
        return {
            "action": "auto_resolve_password",
            "resolved_count": resolved_count,
            "message": f"✅ Auto-resolved {resolved_count} password-related tickets"
        }
    
    def escalate_urgent_tickets(self) -> Dict:
        """Escalate urgent unassigned tickets."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, priority, created_at
            FROM tickets
            WHERE status = 'open'
            AND priority IN ('high', 'urgent')
        """)
        
        tickets = cursor.fetchall()
        escalated_count = 0
        
        for ticket in tickets:
            cursor.execute("""
                UPDATE tickets
                SET priority = 'urgent',
                    description = description || '\n\n⚠️ ESCALATED by Truffle Agent'
                WHERE id = ?
            """, (ticket[0],))
            
            escalated_count += 1
            self.actions_log.append({
                "action": "escalate",
                "ticket_id": ticket[0],
                "reason": "High priority ticket"
            })
        
        conn.commit()
        conn.close()
        
        return {
            "action": "escalate_urgent",
            "escalated_count": escalated_count,
            "message": f"⚠️ Escalated {escalated_count} urgent tickets"
        }
    
    def send_satisfaction_survey(self) -> Dict:
        """Send satisfaction survey for resolved tickets."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, customer_email, resolved_at
            FROM tickets
            WHERE status = 'resolved'
            AND satisfaction_score IS NULL
        """)
        
        tickets = cursor.fetchall()
        survey_count = 0
        
        for ticket in tickets:
            survey_count += 1
            self.actions_log.append({
                "action": "send_survey",
                "ticket_id": ticket[0],
                "email": ticket[1]
            })
        
        conn.close()
        
        return {
            "action": "send_survey",
            "survey_count": survey_count,
            "message": f"📧 Queued {survey_count} satisfaction surveys"
        }
    
    def run_daily_workflow(self) -> Dict:
        """Run all automated workflows."""
        print("🤖 Running daily workflows...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        
        results["actions"].append(self.auto_resolve_password_tickets())
        results["actions"].append(self.escalate_urgent_tickets())
        results["actions"].append(self.send_satisfaction_survey())
        
        return results
    
    def get_logs(self) -> List[Dict]:
        """Get action logs."""
        return self.actions_log

if __name__ == "__main__":
    agent = WorkflowAgent()
    results = agent.run_daily_workflow()
    for action in results["actions"]:
        print(action["message"])
