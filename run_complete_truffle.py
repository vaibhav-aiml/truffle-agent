"""Truffle - Complete AI Support Agent under functional architecture."""

import streamlit as st
import sys
import os
import time
import http.server
import socketserver
import threading
import json
import uuid
from pathlib import Path

# Add paths for backend imports
sys.path.insert(0, os.getcwd())

from backend.config import settings
from backend.config.validation import validate_environment
from backend.agents.truffle_agent import create_agent_context, chat_with_agent
from backend.services.workflow_service import (
    auto_resolve_password_tickets,
    escalate_urgent_tickets,
    send_satisfaction_survey,
    run_daily_workflow,
    get_action_logs
)
from backend.services.cache_service import make_query_cache_key, get_cached_query, set_cached_query
from backend.services.rate_limiter import is_rate_limited
from backend.utils.logger import logger

# 1. Initialize Sentry SDK for error monitoring
if settings.SENTRY_DSN:
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0
        )
        logger.info("Sentry monitoring initialized successfully.")
    except ImportError:
        logger.warning("Sentry SDK packages missing. Crash reporting disabled.")
    except Exception as e:
        logger.error(f"Sentry error handler failed to start: {e}")

# 2. Launch HTTP Daemon Health Check Server on Port 8080
def start_health_check_server(port=8080):
    class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response_data = {"status": "healthy", "version": "1.0.0"}
                self.wfile.write(json.dumps(response_data).encode())
            else:
                self.send_response(404)
                self.end_headers()
        def log_message(self, format, *args):
            pass # Suppress server access logs in stdout
            
    def run():
        try:
            socketserver.TCPServer.allow_reuse_address = True
            with socketserver.TCPServer(("", port), HealthCheckHandler) as httpd:
                logger.info(f"Health check daemon listening on port {port}")
                httpd.serve_forever()
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")

    t = threading.Thread(target=run, daemon=True)
    t.start()

@st.cache_resource
def initialize_health_server():
    start_health_check_server(8080)
    return True

initialize_health_server()

# Validate environment settings on startup
is_valid, config_warnings, config_errors = validate_environment()

st.set_page_config(page_title="Truffle", page_icon="🍄", layout="wide")

st.title("🍄 Truffle")
st.caption("AI Support Agent | RAG + Text-to-SQL + Workflow Automation")

# Render validation alerts
if config_errors:
    for err in config_errors:
        st.error(f"❌ Configuration Error: {err}")
    st.stop()
    
if config_warnings:
    with st.expander("⚠️ System Configuration Warnings (Non-blocking)"):
        for warn in config_warnings:
            st.warning(warn)

# Initialize functional context
@st.cache_resource
def get_agent_context():
    return create_agent_context()

try:
    agent_context = get_agent_context()
    db_path = agent_context["db_path"]
except Exception as e:
    st.error(f"Critical System Initialization Error: {e}")
    st.stop()

# Helper to identify user sessions for rate limiting
def get_user_identifier() -> str:
    if "user_session_id" not in st.session_state:
        st.session_state.user_session_id = str(uuid.uuid4())
    return st.session_state.user_session_id

user_id = get_user_identifier()

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    page = st.radio("Go to:", ["💬 Chat", "🤖 Workflow Agent", "📈 Analytics Dashboard", "📊 Evaluation Dashboard"])
    
    st.markdown("---")
    st.markdown("### Features")
    st.markdown("""
    ✅ **RAG Knowledge Base** - Docs & policy search
    ✅ **Text-to-SQL** - SQLite query execution
    ✅ **Workflow Agent** - Ticket automation
    ✅ **Evaluation** - Accuracy metrics suite
    ✅ **Analytics** - Operational insights
    """)
    st.markdown("---")
    st.caption("Monitoring: Port 8080 `/health` active")

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
        "What subscription plans do you offer?",
        "Show tickets assigned to Bob"
    ]
    
    col1, col2, col3 = st.columns(3)
    for i, ex in enumerate(examples[:6]):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(ex, use_container_width=True, key=f"ex_{i}"):
                st.session_state.quick_question = ex
    
    if "quick_question" in st.session_state:
        query = st.session_state.quick_question
        del st.session_state.quick_question
    else:
        query = st.chat_input("Ask about support or tickets...")
    
    if query:
        # 1. Input Length Validation (prevents prompt stuffing / embedding cost inflation)
        MAX_QUERY_LENGTH = 500
        if len(query) > MAX_QUERY_LENGTH:
            st.error(f"🚨 Query too long ({len(query)} characters). Please keep your question under {MAX_QUERY_LENGTH} characters.")
        # 2. Rate Limiting Check (Blocks query if limit exceeded)
        elif is_rate_limited(user_id):
            st.error("🚨 Rate limit exceeded: You have submitted too many requests in a short period. Please wait before asking another question.")
        else:
            st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)
            
            with st.chat_message("assistant"):
                start_time = time.perf_counter()
                
                with st.spinner("🍄 Thinking..."):
                    # 2. Cache Lookup
                    cache_key = make_query_cache_key(query)
                    cached_res = get_cached_query(cache_key)
                    
                    if cached_res:
                        logger.info(f"Serving cached answer for query: '{query}'")
                        result = cached_res
                        result["from_cache"] = True
                    else:
                        result = chat_with_agent(agent_context, query)
                        result["from_cache"] = False
                        set_cached_query(cache_key, result)
                        
                    st.markdown(result["response"])
                    
                    if result.get("sql"):
                        with st.expander("🔍 View SQL Query"):
                            st.code(result["sql"], language="sql")
                
                end_time = time.perf_counter()
                response_time = end_time - start_time
                if response_time < 0.01:
                    response_time = 0.05
                
                confidence = result.get("confidence", 50)
                if confidence > 100:
                    confidence = confidence / 100
                
                # Display metrics
                col_metric1, col_metric2 = st.columns(2)
                with col_metric1:
                    if confidence >= 90:
                        st.success(f"✅ Confidence: {confidence:.0f}%")
                    elif confidence >= 70:
                        st.info(f"📊 Confidence: {confidence:.0f}%")
                    else:
                        st.warning(f"⚠️ Confidence: {confidence:.0f}%")
                
                with col_metric2:
                    if result.get("from_cache"):
                        st.success("⚡ Response: Cached (Redis)")
                    else:
                        if response_time < 0.5:
                            st.success(f"⚡ Response: {response_time:.2f}s")
                        elif response_time < 1.5:
                            st.info(f"⏱️ Response: {response_time:.2f}s")
                        else:
                            st.warning(f"🐢 Response: {response_time:.2f}s")
            
            st.session_state.messages.append({"role": "assistant", "content": result["response"]})

elif page == "🤖 Workflow Agent":
    st.markdown("## 🤖 Automated Workflow Agent")
    st.markdown("Run automated tasks to manage tickets")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Auto-resolve Password Tickets", use_container_width=True):
            with st.spinner("Processing..."):
                start = time.perf_counter()
                result = auto_resolve_password_tickets(db_path)
                elapsed = time.perf_counter() - start
                st.success(result["message"])
                st.caption(f"Completed in {elapsed:.2f}s")
                st.json(result)
    
    with col2:
        if st.button("⚠️ Escalate Urgent Tickets", use_container_width=True):
            with st.spinner("Processing..."):
                start = time.perf_counter()
                result = escalate_urgent_tickets(db_path)
                elapsed = time.perf_counter() - start
                st.info(result["message"])
                st.caption(f"Completed in {elapsed:.2f}s")
                st.json(result)
    
    with col3:
        if st.button("📧 Send Satisfaction Surveys", use_container_width=True):
            with st.spinner("Processing..."):
                start = time.perf_counter()
                result = send_satisfaction_survey(db_path)
                elapsed = time.perf_counter() - start
                st.info(result["message"])
                st.caption(f"Completed in {elapsed:.2f}s")
                st.json(result)
    
    st.markdown("---")
    st.markdown("### 🚀 Run All Workflows")
    if st.button("▶️ Run Daily Workflow", type="primary"):
        with st.spinner("Running all workflows..."):
            start = time.perf_counter()
            results = run_daily_workflow(db_path)
            elapsed = time.perf_counter() - start
            st.success(f"✅ Daily workflow completed in {elapsed:.2f}s!")
            for action in results["actions"]:
                st.info(action["message"])
    
    st.markdown("---")
    st.markdown("### 📝 Action Log")
    logs = get_action_logs()
    if logs:
        st.json(logs[-10:])
    else:
        st.info("No actions logged yet. Run a workflow to see logs.")

elif page == "📈 Analytics Dashboard":
    from frontend.pages.analytics import show_analytics
    show_analytics()

elif page == "📊 Evaluation Dashboard":
    from frontend.pages.dashboard import show_dashboard
    show_dashboard()
