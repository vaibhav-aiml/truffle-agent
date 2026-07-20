"""Evaluation dashboard displaying dynamic system accuracy metrics."""

import streamlit as st
from pathlib import Path
from backend.evaluation.metrics import run_suite_evaluation
from backend.config import settings
from frontend.components.ui_components import (
    render_page_header,
    render_bento_metrics,
    render_section_divider,
    render_test_results_table,
    render_alert_banner,
)


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
    """Display the evaluation dashboard with the new design system."""
    render_page_header("📊", "Evaluation Dashboard", "Dynamic performance and accuracy calculations")
    
    # Run evaluation suite
    with st.spinner("🔄 Running dynamic test suite evaluation…"):
        suite_results = run_suite_evaluation()
        
    if "error" in suite_results:
        render_alert_banner(f"Failed to run evaluation suite: {suite_results['error']}", "error")
        return

    # ── Performance Metrics (Bento Grid) ──
    accuracy = suite_results["accuracy"]
    acc_accent = "green" if accuracy >= 80 else ("amber" if accuracy >= 60 else "rose")
    
    avg_latency = suite_results["avg_response_time"]
    lat_accent = "green" if avg_latency < 0.5 else ("amber" if avg_latency < 2.0 else "rose")
    
    render_bento_metrics([
        {"value": f"{accuracy:.1f}%", "label": "Test Accuracy", "accent": acc_accent},
        {"value": f"{avg_latency:.3f}s", "label": "Avg Latency", "accent": lat_accent},
        {"value": str(suite_results["total_cases"]), "label": "Tests Executed", "accent": "cyan"},
        {"value": f"{suite_results['passed_cases']}/{suite_results['total_cases']}", "label": "Tests Passed", "accent": "violet"},
    ])

    # ── Database Statistics ──
    db_stats = get_database_stats()
    if "error" not in db_stats:
        render_bento_metrics([
            {"value": str(db_stats["Total Tickets"]), "label": "Total Tickets", "accent": "violet"},
            {"value": str(db_stats["Open Tickets"]), "label": "Open Tickets", "accent": "amber"},
            {"value": db_stats["Resolution Rate"], "label": "Resolution Rate", "accent": "green"},
            {"value": db_stats["Avg Satisfaction"], "label": "Avg Satisfaction", "accent": "cyan"},
        ])
    else:
        render_alert_banner(db_stats["error"], "warning")

    render_section_divider()

    # ── Test Results Table ──
    render_page_header("📝", "Test Execution Log", "Detailed results for each evaluation case")
    render_test_results_table(suite_results["results"])


if __name__ == "__main__":
    show_dashboard()
