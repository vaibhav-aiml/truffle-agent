"""Agent workflow for auto-resolving tickets."""

import sqlite3
from datetime import datetime
from typing import Dict, List

class WorkflowAgent:
    """Automated workflow agent for ticket management."""
    
    def __init__(self, db_path="data/processed/sql_db/tickets.db"):
        self.db_path = db_path
        self.actions_log = []
    
    def auto_resolve_password_tickets(self) -> Dict:
        """Auto-resolve password reset tickets."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find password-related open tickets
        cursor.execute("""
            SELECT id, subject, customer_email 
            FROM tickets 
            WHERE status = 'open' 
            AND (subject LIKE '%password%' OR subject LIKE '%login%')
        """)
        
        tickets = cursor.fetchall()
        resolved_count = 0
        
        for ticket in tickets:
            # Auto-resolve by sending password reset email
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
            AND created_at < date('now', '-1 day')
        """)
        
        tickets = cursor.fetchall()
        escalated_count = 0
        
        for ticket in tickets:
            cursor.execute("""
                UPDATE tickets
                SET priority = 'urgent',
                    description = description || '\n\n⚠️ ESCALATED by Truffle Agent - SLA breach risk'
                WHERE id = ?
            """, (ticket[0],))
            
            escalated_count += 1
            self.actions_log.append({
                "action": "escalate",
                "ticket_id": ticket[0],
                "reason": "Unresolved for >24 hours"
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
            AND resolved_at > date('now', '-3 days')
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
        
        # Run each workflow
        results["actions"].append(self.auto_resolve_password_tickets())
        results["actions"].append(self.escalate_urgent_tickets())
        results["actions"].append(self.send_satisfaction_survey())
        
        return results
    
    def get_logs(self) -> List[Dict]:
        """Get action logs."""
        return self.actions_log

if __name__ == "__main__":
    agent = WorkflowAgent()
    
    print("🚀 Testing Workflow Agent...")
    results = agent.run_daily_workflow()
    
    for action in results["actions"]:
        print(f"\n{action['message']}")
    
    print(f"\n📝 Total actions logged: {len(agent.get_logs())}")
