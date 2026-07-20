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
from frontend.components.ui_components import (
    inject_custom_css,
    render_page_header,
    render_bento_metrics,
    render_chat_message,
    render_chat_metadata,
    render_sql_block,
    render_typing_indicator,
    render_alert_banner,
    render_workflow_card,
    render_result_panel,
    render_action_log_timeline,
    render_section_divider,
    render_sidebar,
)

# ──────────────────────────────────────────────
# 1. Sentry SDK Initialization
# ──────────────────────────────────────────────
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

# ──────────────────────────────────────────────
# 2. Health Check Daemon (Port 8080)
# ──────────────────────────────────────────────
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

# ──────────────────────────────────────────────
# 3. Page Config & CSS Injection
# ──────────────────────────────────────────────
st.set_page_config(page_title="Truffle", page_icon="🍄", layout="wide")
inject_custom_css()

# ──────────────────────────────────────────────
# 4. Environment Validation
# ──────────────────────────────────────────────
is_valid, config_warnings, config_errors = validate_environment()

if config_errors:
    for err in config_errors:
        render_alert_banner(err, "error")
    st.stop()

if config_warnings:
    with st.expander("⚠️ System Warnings (Non-blocking)"):
        for warn in config_warnings:
            render_alert_banner(warn, "warning")

# ──────────────────────────────────────────────
# 5. Agent Context Initialization
# ──────────────────────────────────────────────
@st.cache_resource
def get_agent_context():
    return create_agent_context()

try:
    agent_context = get_agent_context()
    db_path = agent_context["db_path"]
except Exception as e:
    render_alert_banner(f"Critical System Initialization Error: {e}", "error")
    st.stop()

# Session helpers
def get_user_identifier() -> str:
    if "user_session_id" not in st.session_state:
        st.session_state.user_session_id = str(uuid.uuid4())
    return st.session_state.user_session_id

user_id = get_user_identifier()

# ──────────────────────────────────────────────
# 6. Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    page = render_sidebar()

# ──────────────────────────────────────────────
# 7. Page Routing
# ──────────────────────────────────────────────

# ==================== CHAT PAGE ====================
if page == "💬  Chat":
    render_page_header("💬", "Ask Truffle", "Get instant answers from docs and databases")

    # Quick question pills
    examples = [
        "How do I invite team members?",
        "How many open tickets?",
        "Show me high priority tickets",
        "What subscription plans are offered?",
        "Show tickets assigned to Bob",
    ]

    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        with cols[i]:
            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state.quick_question = ex

    st.markdown("")  # spacer

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render past messages with custom bubbles
    for msg in st.session_state.messages:
        render_chat_message(msg["role"], msg["content"])

    # Input handling
    if "quick_question" in st.session_state:
        query = st.session_state.quick_question
        del st.session_state.quick_question
    else:
        query = st.chat_input("Ask about support, tickets, or policies…")

    if query:
        MAX_QUERY_LENGTH = 500
        if len(query) > MAX_QUERY_LENGTH:
            render_alert_banner(
                f"Query too long ({len(query)} chars). Please keep under {MAX_QUERY_LENGTH} characters.",
                "error"
            )
        elif is_rate_limited(user_id):
            render_alert_banner(
                "Rate limit exceeded. Please wait before asking another question.",
                "error"
            )
        else:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": query})
            render_chat_message("user", query)

            # Show typing indicator placeholder
            typing_placeholder = st.empty()
            with typing_placeholder:
                render_typing_indicator()

            start_time = time.perf_counter()

            # Process query
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

            end_time = time.perf_counter()
            response_time = end_time - start_time
            if response_time < 0.01:
                response_time = 0.05

            # Remove typing indicator
            typing_placeholder.empty()

            # Render assistant response
            render_chat_message("assistant", result["response"])

            # Response metadata pills
            confidence = result.get("confidence", 50)
            if confidence > 100:
                confidence = confidence / 100
            render_chat_metadata(
                confidence=confidence,
                response_time=response_time,
                from_cache=result.get("from_cache", False),
                source_type=result.get("type", "")
            )

            # SQL block (if applicable)
            if result.get("sql"):
                render_sql_block(result["sql"])

            st.session_state.messages.append({"role": "assistant", "content": result["response"]})

# ==================== WORKFLOW PAGE ====================
elif page == "🤖  Workflows":
    render_page_header("🤖", "Workflow Agent", "Run automated ticket management tasks")

    # Workflow cards layout
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            render_workflow_card(
                "🔄", "Auto-Resolve Password Tickets",
                "Automatically resolve open tickets related to password resets and login issues.",
                "wf-resolve"
            ),
            unsafe_allow_html=True
        )
        if st.button("Run Auto-Resolve", key="wf_resolve", use_container_width=True):
            with st.spinner("Processing…"):
                start = time.perf_counter()
                result = auto_resolve_password_tickets(db_path)
                elapsed = time.perf_counter() - start
            render_result_panel("✅", result["message"], elapsed, "success")
            st.json(result)

    with col2:
        st.markdown(
            render_workflow_card(
                "⚠️", "Escalate Urgent Tickets",
                "Flag and escalate unresolved tickets with high or urgent priority levels.",
                "wf-escalate"
            ),
            unsafe_allow_html=True
        )
        if st.button("Run Escalation", key="wf_escalate", use_container_width=True):
            with st.spinner("Processing…"):
                start = time.perf_counter()
                result = escalate_urgent_tickets(db_path)
                elapsed = time.perf_counter() - start
            render_result_panel("⚠️", result["message"], elapsed, "warning")
            st.json(result)

    with col3:
        st.markdown(
            render_workflow_card(
                "📧", "Send Satisfaction Surveys",
                "Queue customer satisfaction surveys for resolved tickets without feedback.",
                "wf-survey"
            ),
            unsafe_allow_html=True
        )
        if st.button("Run Surveys", key="wf_survey", use_container_width=True):
            with st.spinner("Processing…"):
                start = time.perf_counter()
                result = send_satisfaction_survey(db_path)
                elapsed = time.perf_counter() - start
            render_result_panel("📧", result["message"], elapsed, "info")
            st.json(result)

    render_section_divider()

    # Run All Workflows CTA
    st.markdown("""
    <div class="run-all-cta">
        <p style="color: #fff; font-weight: 600; font-size: 1rem; margin: 0 0 4px;">
            🚀 Daily Workflow Pipeline
        </p>
        <p style="color: rgba(255,255,255,0.6); font-size: 0.82rem; margin: 0;">
            Execute all automated workflows in sequence
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶️  Run All Workflows", type="primary", use_container_width=True):
        with st.spinner("Running all workflows…"):
            start = time.perf_counter()
            results = run_daily_workflow(db_path)
            elapsed = time.perf_counter() - start
        render_result_panel("🚀", f"Daily workflow pipeline completed", elapsed, "success")
        for action in results["actions"]:
            render_result_panel("→", action["message"], 0, "info")

    render_section_divider()

    # Action Log Timeline
    render_page_header("📋", "Activity Log", "Recent workflow actions and events")
    logs = get_action_logs()
    render_action_log_timeline(logs)

# ==================== ANALYTICS PAGE ====================
elif page == "📈  Analytics":
    from frontend.pages.analytics import show_analytics
    show_analytics()

# ==================== EVALUATION PAGE ====================
elif page == "📊  Evaluation":
    from frontend.pages.dashboard import show_dashboard
    show_dashboard()
