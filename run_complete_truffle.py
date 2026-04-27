"""Truffle - Complete AI Support Agent with all features."""

import streamlit as st
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.getcwd())

from run_agent import TruffleAgent
from backend.agent.workflow_agent import WorkflowAgent

st.set_page_config(page_title="Truffle", page_icon="🍄", layout="wide")

st.title("🍄 Truffle")
st.caption("AI Support Agent | RAG + Text-to-SQL + Workflow Automation")

# Initialize components
@st.cache_resource
def get_agent():
    return TruffleAgent()

@st.cache_resource
def get_workflow():
    return WorkflowAgent()

agent = get_agent()
workflow = get_workflow()

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    page = st.radio("Go to:", ["💬 Chat", "🤖 Workflow Agent", "📊 Evaluation Dashboard"])
    
    st.markdown("---")
    st.markdown("### Features")
    st.markdown("""
    ✅ **RAG Knowledge Base** - Team invites, plans, password
    ✅ **Text-to-SQL** - Complex queries with dates, agents
    ✅ **Workflow Agent** - Auto-resolve, escalate, survey
    ✅ **Evaluation** - Accuracy metrics dashboard
    """)

# Page routing
if page == "💬 Chat":
    st.markdown("## 💬 Ask Truffle")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    examples = [
        "How do I invite team members?",
        "How many open tickets?",
        "Show me high priority tickets",
        "What subscription plans do you offer?"
    ]
    
    cols = st.columns(2)
    for i, ex in enumerate(examples[:4]):
        with cols[i % 2]:
            if st.button(ex, use_container_width=True, key=f"ex_{i}"):
                st.session_state.quick_question = ex
    
    if "quick_question" in st.session_state:
        query = st.session_state.quick_question
        del st.session_state.quick_question
    else:
        query = st.chat_input("Ask about support or tickets...")
    
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        with st.chat_message("assistant"):
            start_time = time.time()
            with st.spinner("🍄 Thinking..."):
                result = agent.chat(query)
                st.markdown(result["response"])
                
                if result.get("sql"):
                    with st.expander("🔍 View SQL Query"):
                        st.code(result["sql"], language="sql")
                
                response_time = time.time() - start_time
                st.success(f"Confidence: {result['confidence']:.0%} | Response: {response_time:.1f}s")
        
        st.session_state.messages.append({"role": "assistant", "content": result["response"]})

elif page == "🤖 Workflow Agent":
    st.markdown("## 🤖 Automated Workflow Agent")
    st.markdown("Run automated tasks to manage tickets")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Auto-resolve Password Tickets", use_container_width=True):
            with st.spinner("Processing..."):
                result = workflow.auto_resolve_password_tickets()
                st.success(result["message"])
                st.json(result)
    
    with col2:
        if st.button("⚠️ Escalate Urgent Tickets", use_container_width=True):
            with st.spinner("Processing..."):
                result = workflow.escalate_urgent_tickets()
                st.info(result["message"])
                st.json(result)
    
    with col3:
        if st.button("📧 Send Satisfaction Surveys", use_container_width=True):
            with st.spinner("Processing..."):
                result = workflow.send_satisfaction_survey()
                st.info(result["message"])
                st.json(result)
    
    st.markdown("---")
    st.markdown("### 🚀 Run All Workflows")
    if st.button("▶️ Run Daily Workflow", type="primary"):
        with st.spinner("Running all workflows..."):
            results = workflow.run_daily_workflow()
            st.success("✅ Daily workflow completed!")
            for action in results["actions"]:
                st.info(action["message"])
    
    st.markdown("---")
    st.markdown("### 📝 Action Log")
    logs = workflow.get_logs()
    if logs:
        st.json(logs[-10:])
    else:
        st.info("No actions logged yet. Run a workflow to see logs.")

elif page == "📊 Evaluation Dashboard":
    from frontend.pages.dashboard import show_dashboard
    show_dashboard()
