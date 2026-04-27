"""Run Truffle Streamlit App - Run this from truffle-agent folder."""

import streamlit as st
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

from run_agent import TruffleAgent

st.set_page_config(page_title="Truffle", page_icon="🍄", layout="wide")

st.title("🍄 Truffle")
st.caption("AI Support Agent | RAG Knowledge Base + Text-to-SQL Database")

@st.cache_resource
def get_agent():
    return TruffleAgent()

try:
    agent = get_agent()
    st.sidebar.success("✅ Truffle Ready")
except Exception as e:
    st.sidebar.error(f"Error: {e}")
    agent = None

with st.sidebar:
    st.markdown("### Features")
    st.markdown("""
    **📚 Knowledge Base**
    - Team invites | Subscription plans
    - Password reset | Refunds | Mobile app
    
    **🗄️ Database Queries**
    - Ticket counts | Priority tickets
    - Satisfaction scores
    """)
    
    examples = [
        "How do I invite team members?",
        "How many open tickets?",
        "Show me high priority tickets",
        "What subscription plans do you offer?"
    ]
    
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.quick_question = ex

st.markdown("## 💬 Ask Truffle")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if "quick_question" in st.session_state:
    query = st.session_state.quick_question
    del st.session_state.quick_question
else:
    query = st.chat_input("Ask about support or tickets...")

if query and agent:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    
    with st.chat_message("assistant"):
        with st.spinner("🍄 Thinking..."):
            result = agent.chat(query)
            st.markdown(result["response"])
            
            if result.get("sql"):
                with st.expander("🔍 SQL Query"):
                    st.code(result["sql"], language="sql")
            
            st.success(f"Confidence: {result['confidence']:.0%}")
    
    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
