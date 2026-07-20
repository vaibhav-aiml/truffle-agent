"""Evaluation dashboard displaying dynamic system accuracy metrics."""

import streamlit as st
import sqlite3
from pathlib import Path
from backend.evaluation.metrics import run_suite_evaluation
from backend.config import settings

def get_database_stats() -> dict:
    """Get database statistics."""
    db_path = settings.DB_PATH
    if not db_path.exists():
        return {"error": "Database not found"}
    
    try:
        from backend.services.sql_service import get_db_connection
        with get_db_connection(str(db_path)) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM tickets")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
            open_tickets = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(satisfaction_score) FROM tickets WHERE satisfaction_score IS NOT NULL")
            avg_satisfaction = cursor.fetchone()[0] or 0.0
        
        resolution_rate = f"{(total - open_tickets) / max(1, total) * 100:.0f}%"
        
        return {
            "Total Tickets": total,
            "Open Tickets": open_tickets,
            "Resolution Rate": resolution_rate,
            "Avg Satisfaction": f"{avg_satisfaction:.1f}/5.0"
        }
    except Exception as e:
        return {"error": f"Database read error: {e}"}

def show_dashboard():
    """Display the evaluation dashboard."""
    st.markdown("## 📊 Truffle Evaluation Dashboard")
    st.markdown("Dynamic performance and accuracy calculations matching the test cases.")
    
    # 1. Trigger Suite Run
    with st.spinner("🔄 Running dynamic test suite evaluation..."):
        suite_results = run_suite_evaluation()
        
    if "error" in suite_results:
        st.error(f"Failed to run evaluation suite: {suite_results['error']}")
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Dynamic System Performance")
        st.metric("Test Accuracy Score", f"{suite_results['accuracy']:.1f}%")
        st.metric("Avg Latency per Query", f"{suite_results['avg_response_time']:.3f}s")
        st.metric("Tests Executed", f"{suite_results['total_cases']}")
        st.metric("Tests Passed", f"{suite_results['passed_cases']}/{suite_results['total_cases']}")
    
    with col2:
        st.markdown("### 🗄️ Database Statistics")
        db_stats = get_database_stats()
        if "error" not in db_stats:
            for key, value in db_stats.items():
                st.metric(key, value)
        else:
            st.warning(db_stats["error"])
            
    st.markdown("---")
    st.markdown("### 📈 Test Cases Execution Detail Log")
    
    for case in suite_results["results"]:
        status_icon = "✅" if case["passed"] else "❌"
        
        with st.expander(f"{status_icon} Case #{case['id']} - Query: \"{case['query']}\""):
            st.markdown(f"**Expected Handler:** `{case['expected_source']}`")
            st.markdown(f"**Actual Routed Handler:** `{case['actual_source']}`")
            st.markdown(f"**Execution Latency:** `{case['latency']:.4f}s`")
            st.markdown(f"**Detail:** {case['details']}")

if __name__ == "__main__":
    show_dashboard()
