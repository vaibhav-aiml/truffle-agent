"""Truffle - Complete with RAG + Text-to-SQL - Fixed imports."""

import streamlit as st
import sys
import os

# Add the parent directory to path so backend can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import works
from backend.agents.truffle_agent import TruffleAgent

# Initialize agent
@st.cache_resource
def get_agent():
    return TruffleAgent()

st.set_page_config(page_title="Truffle", page_icon="🍄", layout="wide")

st.title("🍄 Truffle")
st.caption("AI Support Agent | RAG + Text-to-SQL")

# Initialize
try:
    agent = get_agent()
    st.sidebar.success("✅ Truffle Ready")
except Exception as e:
    st.sidebar.error(f"Error: {e}")
    agent = None

# Sidebar
with st.sidebar:
    st.markdown("### Capabilities")
    st.markdown("""
    **📚 Knowledge Base (RAG)**
    - Team management
    - Subscription plans
    - Password reset
    - Refund policy
    - Mobile app info
    
    **🗄️ Database (Text-to-SQL)**
    - Ticket counts
    - Priority tickets
    - Agent assignments
    - Satisfaction scores
    """)
    
    st.markdown("---")
    st.markdown("### Example Questions")
    
    examples = [
        "How do I invite team members?",
        "How many open tickets?",
        "Show me high priority tickets",
        "Average satisfaction score?",
        "How do I cancel my subscription?",
        "Show urgent tickets"
    ]
    
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.quick_question = ex

# Chat interface
st.markdown("## 💬 Ask Truffle")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle quick question
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
        with st.spinner("🍄 Truffle is thinking..."):
            result = agent.chat(query)
            st.markdown(result["response"])
            
            # Show SQL if applicable
            if result.get("sql"):
                with st.expander("🔍 View SQL Query"):
                    st.code(result["sql"], language="sql")
            
            # Show confidence
            if result["confidence"] >= 90:
                st.success(f"Confidence: {result['confidence']:.0%}")
            elif result["confidence"] >= 70:
                st.info(f"Confidence: {result['confidence']:.0%}")
            else:
                st.warning(f"Confidence: {result['confidence']:.0%}")
            
            # Show source
            if result.get("sources"):
                with st.expander("📚 Source"):
                    for src in result["sources"]:
                        st.markdown(f"- {src}")
    
    st.session_state.messages.append({"role": "assistant", "content": result["response"]})

# Footer
st.markdown("---")
st.markdown("🍄 **Truffle** | RAG Knowledge Base + Text-to-SQL Database Query")
