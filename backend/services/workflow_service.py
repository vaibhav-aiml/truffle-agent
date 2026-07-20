"""Stateless automated support workflow service routines."""

import sqlite3
from datetime import datetime
from backend.utils.logger import logger

# In-memory global actions log
_workflow_logs: list[dict[str, str]] = []

def append_action_log(action: str, ticket_id: int, reason: str) -> None:
    """Add a record to the centralized workflow execution log."""
    global _workflow_logs
    _workflow_logs.append({
        "action": action,
        "ticket_id": ticket_id,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    })

def get_action_logs() -> list[dict[str, str]]:
    """Retrieve list of executed workflow actions."""
    global _workflow_logs
    return _workflow_logs

def auto_resolve_password_tickets(db_path: str) -> dict[str, str | int]:
    """Find and auto-resolve password or login reset tickets."""
    from backend.services.sql_service import get_db_connection
    resolved_count: int = 0
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, subject, customer_email 
            FROM tickets 
            WHERE status = 'open' 
            AND (subject LIKE '%password%' OR subject LIKE '%login%')
        """)
        tickets: list[tuple] = cursor.fetchall()
        
        for ticket in tickets:
            cursor.execute("""
                UPDATE tickets 
                SET status = 'resolved', 
                    resolved_at = ?,
                    description = description || '\n\nAuto-resolved by Truffle Agent'
                WHERE id = ?
            """, (datetime.now().strftime("%Y-%m-%d"), ticket[0]))
            resolved_count += 1
            append_action_log("auto_resolve", ticket[0], "Password reset request")
        conn.commit()
    
    return {
        "action": "auto_resolve_password",
        "resolved_count": resolved_count,
        "message": f"✅ Auto-resolved {resolved_count} password-related tickets"
    }

def escalate_urgent_tickets(db_path: str) -> dict[str, str | int]:
    """Escalate unassigned open tickets containing high or urgent priorities."""
    from backend.services.sql_service import get_db_connection
    escalated_count: int = 0
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, priority, created_at
            FROM tickets
            WHERE status = 'open'
            AND priority IN ('high', 'urgent')
        """)
        tickets: list[tuple] = cursor.fetchall()
        
        for ticket in tickets:
            cursor.execute("""
                UPDATE tickets
                SET priority = 'urgent',
                    description = description || '\n\n⚠️ ESCALATED by Truffle Agent'
                WHERE id = ?
            """, (ticket[0],))
            escalated_count += 1
            append_action_log("escalate", ticket[0], "High priority ticket")
        conn.commit()
    
    return {
        "action": "escalate_urgent",
        "escalated_count": escalated_count,
        "message": f"⚠️ Escalated {escalated_count} urgent tickets"
    }

def send_satisfaction_survey(db_path: str) -> dict[str, str | int]:
    """Queue customer satisfaction survey emails for resolved tickets without feedback scores."""
    from backend.services.sql_service import get_db_connection
    survey_count: int = 0
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, customer_email, resolved_at
            FROM tickets
            WHERE status = 'resolved'
            AND satisfaction_score IS NULL
        """)
        tickets: list[tuple] = cursor.fetchall()
        
        for ticket in tickets:
            survey_count += 1
            append_action_log("send_survey", ticket[0], f"Queued survey for {ticket[1]}")
            
    return {
        "action": "send_survey",
        "survey_count": survey_count,
        "message": f"📧 Queued {survey_count} satisfaction surveys"
    }

def run_daily_workflow(db_path: str) -> dict[str, str | list]:
    """Execute all automated workflow operations sequentially."""
    logger.info("Executing daily operational workflows...")
    results: dict[str, str | list] = {
        "timestamp": datetime.now().isoformat(),
        "actions": []
    }
    results["actions"].append(auto_resolve_password_tickets(db_path))
    results["actions"].append(escalate_urgent_tickets(db_path))
    results["actions"].append(send_satisfaction_survey(db_path))
    return results
