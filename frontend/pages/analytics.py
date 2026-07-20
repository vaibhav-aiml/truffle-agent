"""Analytics dashboard visualization page for ticket statistics."""

import streamlit as st
import pandas as pd
from backend.config import settings
from frontend.components.ui_components import (
    render_page_header,
    render_bento_metrics,
    render_section_divider,
    render_alert_banner,
)

# Design system color palette for charts
CHART_COLORS = {
    "primary": "#a78bfa",
    "secondary": "#67e8f9",
    "green": "#34d399",
    "amber": "#fbbf24",
    "rose": "#fb7185",
    "muted": "#475569",
    "surface": "#12121a",
    "deep": "#0a0a0f",
    "text": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "glass_border": "rgba(255,255,255,0.06)",
}

STATUS_COLORS = {
    "open": "#67e8f9",
    "resolved": "#34d399",
    "closed": "#a78bfa",
    "pending": "#fbbf24",
    "in_progress": "#818cf8",
}

PRIORITY_COLORS = {
    "low": "#34d399",
    "medium": "#67e8f9",
    "high": "#fbbf24",
    "urgent": "#fb7185",
}

CATEGORY_COLORS = ["#a78bfa", "#67e8f9", "#34d399", "#fbbf24", "#fb7185", "#818cf8", "#f0abfc"]


def _get_plotly_layout(title: str = "", height: int = 350) -> dict:
    """Return a consistent dark-themed Plotly layout config."""
    return dict(
        title=dict(text=title, font=dict(size=14, color=CHART_COLORS["text"], family="Inter"), x=0, y=0.98) if title else None,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=CHART_COLORS["text_secondary"], size=12),
        height=height,
        margin=dict(l=20, r=20, t=40 if title else 20, b=20),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.04)",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.04)",
            tickfont=dict(size=11),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=CHART_COLORS["text_secondary"]),
        ),
        hoverlabel=dict(
            bgcolor=CHART_COLORS["surface"],
            font_size=12,
            font_family="Inter",
            bordercolor=CHART_COLORS["glass_border"],
        ),
    )


def show_analytics():
    """Display the analytics dashboard with Plotly charts and bento metrics."""
    render_page_header("📈", "Analytics & Insights", "Real-time operational visualizations from the tickets database")
    
    db_path = settings.DB_PATH
    
    if not db_path.exists():
        render_alert_banner(
            "Database file not found. Please run the database setup first.",
            "warning"
        )
        return
        
    try:
        from backend.services.sql_service import get_db_connection
        with get_db_connection(str(db_path)) as conn:
            df = pd.read_sql_query("SELECT * FROM tickets", conn)
    except Exception as e:
        render_alert_banner(f"Error accessing database: {e}", "error")
        return
        
    if df.empty:
        render_alert_banner("No tickets found in the database.", "info")
        return

    # ── KPI Metrics Row ──
    total_tickets = len(df)
    open_tickets = len(df[df['status'] == 'open'])
    resolved_tickets = len(df[df['status'].isin(['resolved', 'closed'])])
    avg_sat = df['satisfaction_score'].mean()
    
    render_bento_metrics([
        {"value": str(total_tickets), "label": "Total Tickets", "accent": "violet"},
        {"value": str(open_tickets), "label": "Active Open", "accent": "cyan"},
        {"value": str(resolved_tickets), "label": "Resolved / Closed", "accent": "green"},
        {"value": f"{avg_sat:.2f}/5.0" if pd.notna(avg_sat) else "N/A", "label": "Avg Satisfaction", "accent": "amber"},
    ])

    render_section_divider()

    # ── Try to import plotly; fall back to Streamlit charts if unavailable ──
    try:
        import plotly.graph_objects as go
        has_plotly = True
    except ImportError:
        has_plotly = False

    # ── Row 1: Status & Priority ──
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">📊 Tickets by Status</div>
        """, unsafe_allow_html=True)
        
        status_counts = df['status'].value_counts()
        
        if has_plotly:
            colors = [STATUS_COLORS.get(s, CHART_COLORS["muted"]) for s in status_counts.index]
            fig = go.Figure(go.Bar(
                x=status_counts.values,
                y=status_counts.index,
                orientation='h',
                marker=dict(
                    color=colors,
                    line=dict(width=0),
                    cornerradius=6,
                ),
                text=status_counts.values,
                textposition='auto',
                textfont=dict(color="#fff", size=12, family="Inter"),
            ))
            fig.update_layout(**_get_plotly_layout(height=280))
            fig.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.bar_chart(status_counts)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_right:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">🚨 Tickets by Priority</div>
        """, unsafe_allow_html=True)
        
        priority_order = ['low', 'medium', 'high', 'urgent']
        p_counts = df['priority'].value_counts().reindex(priority_order, fill_value=0)
        
        if has_plotly:
            colors = [PRIORITY_COLORS.get(p, CHART_COLORS["muted"]) for p in p_counts.index]
            fig = go.Figure(go.Bar(
                x=p_counts.index,
                y=p_counts.values,
                marker=dict(
                    color=colors,
                    line=dict(width=0),
                    cornerradius=6,
                ),
                text=p_counts.values,
                textposition='auto',
                textfont=dict(color="#fff", size=12, family="Inter"),
            ))
            fig.update_layout(**_get_plotly_layout(height=280))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.bar_chart(p_counts)
        
        st.markdown("</div>", unsafe_allow_html=True)

    render_section_divider()

    # ── Row 2: Agent Workload & Categories ──
    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">🤖 Agent Workload</div>
        """, unsafe_allow_html=True)
        
        agent_counts = df['assigned_to'].value_counts()
        
        if has_plotly:
            fig = go.Figure(go.Bar(
                x=agent_counts.values,
                y=agent_counts.index,
                orientation='h',
                marker=dict(
                    color=CHART_COLORS["primary"],
                    line=dict(width=0),
                    cornerradius=6,
                ),
                text=agent_counts.values,
                textposition='auto',
                textfont=dict(color="#fff", size=12, family="Inter"),
            ))
            fig.update_layout(**_get_plotly_layout(height=300))
            fig.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.bar_chart(agent_counts)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_right2:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">📂 Ticket Categories</div>
        """, unsafe_allow_html=True)
        
        if 'category' not in df.columns:
            categories = []
            for sub in df['subject'].astype(str):
                sub_lower = sub.lower()
                if 'login' in sub_lower or 'password' in sub_lower or 'account' in sub_lower:
                    categories.append('Account')
                elif 'billing' in sub_lower or 'charge' in sub_lower or 'invoice' in sub_lower or 'subscription' in sub_lower:
                    categories.append('Billing')
                elif 'api' in sub_lower or 'integration' in sub_lower:
                    categories.append('Developer')
                elif 'bug' in sub_lower or 'crash' in sub_lower or 'performance' in sub_lower:
                    categories.append('Technical')
                else:
                    categories.append('General')
            df['category'] = categories
            
        cat_counts = df['category'].value_counts()
        
        if has_plotly:
            fig = go.Figure(go.Pie(
                labels=cat_counts.index,
                values=cat_counts.values,
                hole=0.55,
                marker=dict(
                    colors=CATEGORY_COLORS[:len(cat_counts)],
                    line=dict(color=CHART_COLORS["deep"], width=2),
                ),
                textinfo='label+percent',
                textfont=dict(size=11, family="Inter", color="#fff"),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            ))
            fig.update_layout(**_get_plotly_layout(height=300))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.bar_chart(cat_counts)
        
        st.markdown("</div>", unsafe_allow_html=True)

    render_section_divider()

    # ── Row 3: Timeline ──
    if 'created_at' in df.columns:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">📅 Ticket Volume Over Time</div>
        """, unsafe_allow_html=True)
        
        df['created_date'] = pd.to_datetime(df['created_at'])
        timeline = df.groupby('created_date').size().reset_index(name='count')
        timeline = timeline.sort_values('created_date')
        
        if has_plotly:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timeline['created_date'],
                y=timeline['count'],
                mode='lines+markers',
                line=dict(color=CHART_COLORS["primary"], width=2.5, shape='spline'),
                marker=dict(size=6, color=CHART_COLORS["primary"], line=dict(width=1, color="#fff")),
                fill='tozeroy',
                fillcolor='rgba(167, 139, 250, 0.08)',
                hovertemplate="<b>%{x|%b %d}</b><br>Tickets: %{y}<extra></extra>",
            ))
            fig.update_layout(**_get_plotly_layout(height=300))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.line_chart(timeline.set_index('created_date')['count'])
        
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Export Button ──
    render_section_divider()
    
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📥  Export Ticket Data (CSV)",
        data=csv_data,
        file_name="truffle_tickets_export.csv",
        mime="text/csv",
        use_container_width=True,
    )


if __name__ == "__main__":
    show_analytics()
