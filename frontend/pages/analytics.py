"""Analytics dashboard visualization page for ticket statistics."""

import streamlit as st
import sqlite3
import pandas as pd
from backend.config import settings

def show_analytics():
    st.markdown("## 📈 Truffle Analytics & Insights")
    st.markdown("Real-time operational visualizations from tickets database.")
    
    db_path = settings.DB_PATH
    
    if not db_path.exists():
        st.warning("⚠️ Database file not found. Please run the database setup or trigger a daily workflow to generate ticket records.")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM tickets", conn)
        conn.close()
    except Exception as e:
        st.error(f"Error accessing database: {e}")
        return
        
    if df.empty:
        st.info("No tickets found in the database to display.")
        return
        
    # Metrics Row
    total_tickets = len(df)
    open_tickets = len(df[df['status'] == 'open'])
    resolved_tickets = len(df[df['status'].isin(['resolved', 'closed'])])
    avg_sat = df['satisfaction_score'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tickets Logged", f"{total_tickets}")
    col2.metric("Active Open Tickets", f"{open_tickets}")
    col3.metric("Resolved / Closed", f"{resolved_tickets}")
    col4.metric("Avg Satisfaction Score", f"{avg_sat:.2f}/5.0" if pd.notna(avg_sat) else "N/A")
    
    st.markdown("---")
    
    # Grid Row 1: Status & Priority
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 📊 Tickets by Status")
        status_counts = df['status'].value_counts()
        st.bar_chart(status_counts)
        
    with col_right:
        st.markdown("### 🚨 Tickets by Priority")
        priority_order = ['low', 'medium', 'high', 'urgent']
        p_counts = df['priority'].value_counts().reindex(priority_order, fill_value=0)
        st.bar_chart(p_counts)
        
    st.markdown("---")
    
    # Grid Row 2: Workloads and Categories
    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        st.markdown("### 🤖 Agent Workload Distribution")
        agent_counts = df['assigned_to'].value_counts()
        st.bar_chart(agent_counts)
        
    with col_right2:
        st.markdown("### 📂 Ticket Categories")
        if 'category' not in df.columns:
            # Generate categories dynamically if not found
            categories = []
            for sub in df['subject'].astype(str):
                sub_lower = sub.lower()
                if 'login' in sub_lower or 'password' in sub_lower or 'account' in sub_lower:
                    categories.append('account')
                elif 'billing' in sub_lower or 'charge' in sub_lower or 'invoice' in sub_lower or 'subscription' in sub_lower:
                    categories.append('billing')
                elif 'api' in sub_lower or 'integration' in sub_lower:
                    categories.append('developer')
                elif 'bug' in sub_lower or 'crash' in sub_lower or 'performance' in sub_lower:
                    categories.append('technical')
                else:
                    categories.append('general')
            df['category'] = categories
            
        cat_counts = df['category'].value_counts()
        st.bar_chart(cat_counts)
        
    st.markdown("---")
    
    # Grid Row 3: Timelines
    st.markdown("### 📅 Ticket Volume Trends Over Time")
    if 'created_at' in df.columns:
        df['created_date'] = pd.to_datetime(df['created_at'])
        timeline = df.groupby('created_date').size()
        st.line_chart(timeline)

if __name__ == "__main__":
    show_analytics()
