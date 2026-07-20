"""Reusable UI component functions for the Truffle design system."""

import streamlit as st
from pathlib import Path
import html


def inject_custom_css():
    """Load the custom CSS design system and Google Fonts into the Streamlit app."""
    css_path = Path(__file__).parent.parent / "static" / "style.css"
    
    fonts_html = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    """
    st.markdown(fonts_html, unsafe_allow_html=True)
    
    if css_path.exists():
        css_content = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_page_header(icon: str, title: str, subtitle: str):
    """Render a styled page header with icon, title, and subtitle."""
    st.markdown(f"""
    <div class="page-header">
        <div class="title">{icon} {html.escape(title)}</div>
        <p class="subtitle">{html.escape(subtitle)}</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(value: str, label: str, accent: str = "violet") -> str:
    """Return HTML for a single animated metric card.
    
    Args:
        value: The display value (e.g. "94.2%", "127")
        label: The label below the value
        accent: Color accent - one of 'violet', 'green', 'cyan', 'amber', 'rose'
    """
    return f"""
    <div class="metric-card accent-{accent}">
        <div class="metric-value">{html.escape(str(value))}</div>
        <div class="metric-label">{html.escape(label)}</div>
    </div>
    """


def render_bento_metrics(metrics: list[dict], columns: int = 4):
    """Render a row of metric cards in a bento grid layout.
    
    Args:
        metrics: List of dicts with keys 'value', 'label', 'accent'
        columns: Number of grid columns (2, 3, or 4)
    """
    cards_html = "".join(
        render_metric_card(m["value"], m["label"], m.get("accent", "violet"))
        for m in metrics
    )
    st.markdown(
        f'<div class="bento-grid bento-grid-{columns}">{cards_html}</div>',
        unsafe_allow_html=True
    )


def render_chat_message(role: str, content: str):
    """Render a custom-styled chat bubble with avatar.
    
    Args:
        role: 'user' or 'assistant'
        content: The message text (can contain markdown, will be escaped)
    """
    avatar = "👤" if role == "user" else "🍄"
    css_class = role
    
    # Allow basic line breaks but escape HTML
    safe_content = html.escape(str(content)).replace("\n", "<br>")
    
    st.markdown(f"""
    <div class="chat-bubble {css_class}">
        <div class="chat-avatar">{avatar}</div>
        <div class="chat-content">{safe_content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_chat_metadata(confidence: float, response_time: float, from_cache: bool, source_type: str = ""):
    """Render response metadata as styled pill badges below a chat message."""
    pills = []
    
    # Confidence pill
    if confidence >= 90:
        pills.append(f'<span class="meta-pill success">✦ {confidence:.0f}% confidence</span>')
    elif confidence >= 70:
        pills.append(f'<span class="meta-pill info">✦ {confidence:.0f}% confidence</span>')
    else:
        pills.append(f'<span class="meta-pill warning">✦ {confidence:.0f}% confidence</span>')
    
    # Latency pill
    if from_cache:
        pills.append('<span class="meta-pill success">⚡ cached</span>')
    elif response_time < 0.5:
        pills.append(f'<span class="meta-pill success">⚡ {response_time:.2f}s</span>')
    elif response_time < 1.5:
        pills.append(f'<span class="meta-pill info">⏱ {response_time:.2f}s</span>')
    else:
        pills.append(f'<span class="meta-pill warning">⏱ {response_time:.2f}s</span>')
    
    # Source type pill
    if source_type:
        type_label = source_type.upper()
        pills.append(f'<span class="meta-pill info">◈ {type_label}</span>')
    
    st.markdown(f'<div class="chat-meta">{"".join(pills)}</div>', unsafe_allow_html=True)


def render_sql_block(sql: str):
    """Render a SQL query in a styled code block."""
    safe_sql = html.escape(str(sql))
    st.markdown(f"""
    <div class="sql-block">
        <div class="sql-header">Generated SQL Query</div>
        <code>{safe_sql}</code>
    </div>
    """, unsafe_allow_html=True)


def render_typing_indicator():
    """Render an animated typing indicator (three pulsing dots)."""
    st.markdown("""
    <div class="chat-bubble assistant">
        <div class="chat-avatar">🍄</div>
        <div class="typing-indicator">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(text: str, badge_type: str = "info") -> str:
    """Return HTML for a status badge pill.
    
    Args:
        text: Badge label text
        badge_type: One of 'success', 'warning', 'error', 'info'
    """
    return f'<span class="status-badge badge-{badge_type}">{html.escape(text)}</span>'


def render_alert_banner(message: str, alert_type: str = "info"):
    """Render a styled alert banner.
    
    Args:
        message: Alert message text
        alert_type: One of 'success', 'warning', 'error', 'info'
    """
    icons = {
        "success": "✓",
        "warning": "⚠",
        "error": "✕",
        "info": "ℹ"
    }
    icon = icons.get(alert_type, "ℹ")
    st.markdown(f"""
    <div class="alert-banner alert-{alert_type}">
        <span style="font-size: 1.1rem;">{icon}</span>
        <span>{html.escape(message)}</span>
    </div>
    """, unsafe_allow_html=True)


def render_workflow_card(icon: str, title: str, description: str, card_class: str = "") -> str:
    """Return HTML for a workflow action card.
    
    Args:
        icon: Emoji icon for the card
        title: Card title
        description: Card description text
        card_class: Additional CSS class (e.g. 'wf-resolve', 'wf-escalate', 'wf-survey')
    """
    return f"""
    <div class="workflow-card {card_class}">
        <div class="wf-icon">{icon}</div>
        <div class="wf-title">{html.escape(title)}</div>
        <div class="wf-desc">{html.escape(description)}</div>
    </div>
    """


def render_result_panel(icon: str, message: str, elapsed: float, panel_type: str = "success"):
    """Render a styled result panel after workflow execution."""
    st.markdown(f"""
    <div class="result-panel result-{panel_type}">
        <span class="result-icon">{icon}</span>
        <span class="result-text">{html.escape(message)}</span>
        <div class="result-time">Completed in {elapsed:.2f}s</div>
    </div>
    """, unsafe_allow_html=True)


def render_action_log_timeline(logs: list[dict]):
    """Render action logs as a styled vertical timeline."""
    if not logs:
        st.markdown("""
        <div class="glass-card" style="text-align: center; color: var(--text-muted); padding: 32px;">
            <p style="font-size: 1.3rem; margin-bottom: 8px;">📋</p>
            <p style="font-size: 0.88rem;">No actions logged yet. Run a workflow to see activity.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    items_html = ""
    for i, log in enumerate(reversed(logs[-10:])):
        action = html.escape(str(log.get("action", "unknown")))
        ticket_id = log.get("ticket_id", "?")
        reason = html.escape(str(log.get("reason", "")))
        timestamp = html.escape(str(log.get("timestamp", "")))
        
        action_labels = {
            "auto_resolve": "Auto-Resolved",
            "escalate": "Escalated",
            "send_survey": "Survey Queued"
        }
        label = action_labels.get(action, action)
        
        items_html += f"""
        <div class="timeline-item" style="animation-delay: {i * 0.05}s;">
            <div class="tl-action">{label} — Ticket #{ticket_id}</div>
            <div class="tl-detail">{reason}</div>
            <div class="tl-time">{timestamp}</div>
        </div>
        """
    
    st.markdown(f'<div class="timeline">{items_html}</div>', unsafe_allow_html=True)


def render_section_divider():
    """Render a subtle gradient section divider."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_chart_container(title: str, icon: str = "📊"):
    """Return an HTML string that opens a chart container div. Must be paired with close_chart_container."""
    return f"""
    <div class="chart-container">
        <div class="chart-title">{icon} {html.escape(title)}</div>
    """


def render_sidebar():
    """Render the complete custom sidebar with navigation, features, and footer."""
    # Brand
    st.markdown("""
    <div class="sidebar-brand">
        <div class="logo">🍄</div>
        <div class="name">Truffle</div>
        <div class="tagline">AI Support Agent</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Navigation using Streamlit radio (we style it with CSS)
    st.markdown("""
    <p style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; 
              color: var(--text-muted); padding: 0 16px; margin-bottom: 4px; font-weight: 600;">
        Navigation
    </p>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "nav",
        ["💬  Chat", "🤖  Workflows", "📈  Analytics", "📊  Evaluation"],
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Feature tags
    st.markdown("""
    <p style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; 
              color: var(--text-muted); padding: 0 16px; margin-bottom: 8px; font-weight: 600;">
        Capabilities
    </p>
    <div class="feature-tags">
        <span class="feature-tag"><span class="dot"></span> RAG Search</span>
        <span class="feature-tag"><span class="dot"></span> Text-to-SQL</span>
        <span class="feature-tag"><span class="dot"></span> Workflows</span>
        <span class="feature-tag"><span class="dot"></span> Evaluation</span>
        <span class="feature-tag"><span class="dot"></span> Analytics</span>
        <span class="feature-tag"><span class="dot"></span> Caching</span>
        <span class="feature-tag"><span class="dot"></span> Rate Limiting</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="sidebar-footer">
        <span class="health-dot"></span> Health Check Active<br>
        <span style="opacity: 0.5; font-size: 0.65rem;">Port 8080 · /health</span>
    </div>
    """, unsafe_allow_html=True)
    
    return page


def render_test_results_table(results: list[dict]):
    """Render test case results as a styled HTML table."""
    if not results:
        return
    
    rows_html = ""
    for case in results:
        status = "✅" if case["passed"] else "❌"
        badge_class = "badge-success" if case["passed"] else "badge-error"
        badge_text = "PASS" if case["passed"] else "FAIL"
        
        query = html.escape(str(case.get("query", "")))
        expected = html.escape(str(case.get("expected_source", "")))
        actual = html.escape(str(case.get("actual_source", "")))
        latency = case.get("latency", 0)
        details = html.escape(str(case.get("details", "")))
        
        rows_html += f"""
        <tr>
            <td>{status} <span class="status-badge {badge_class}">{badge_text}</span></td>
            <td style="color: var(--text-primary); font-weight: 500;">#{case.get('id', '?')}</td>
            <td>{query}</td>
            <td><code style="color: var(--secondary); font-size: 0.78rem;">{expected}</code></td>
            <td><code style="color: var(--primary); font-size: 0.78rem;">{actual}</code></td>
            <td>{latency:.3f}s</td>
        </tr>
        <tr>
            <td colspan="6" style="padding: 2px 16px 12px; font-size: 0.78rem; color: var(--text-muted); border-bottom: 1px solid var(--glass-border);">
                {details}
            </td>
        </tr>
        """
    
    st.markdown(f"""
    <div style="overflow-x: auto;">
    <table class="test-results-table">
        <thead>
            <tr>
                <th>Status</th>
                <th>ID</th>
                <th>Query</th>
                <th>Expected</th>
                <th>Actual</th>
                <th>Latency</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)
