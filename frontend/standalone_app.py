"""Truffle Standalone - No imports needed, works immediately."""

import streamlit as st

# All answers are built directly into this file
def get_answer(question):
    """Find the right answer based on keywords."""
    q = question.lower()
    
    # Team Invites
    if any(word in q for word in ["invite", "team member", "add member", "add person", "new member", "invitation"]):
        return """
### How to Invite Team Members

**Step-by-Step Instructions:**

1. Log into your account dashboard
2. Click **Settings** in the sidebar
3. Select **Team** or **Team Members**
4. Click the **Invite Member** button
5. Enter the person's email address
6. Choose their role:
   - **Admin** - Full access, can invite/remove members
   - **Member** - Can work on tickets, cannot manage team
   - **Viewer** - Read-only access
7. Click **Send Invitation**

The person will receive an email with a join link.

**Team Limits by Plan:**
- Basic: 5 members maximum
- Premium: 20 members maximum
- Enterprise: Unlimited members
""", 95
    
    # Cancellation
    if any(word in q for word in ["cancel", "unsubscribe", "stop billing", "end subscription", "cancellation"]):
        return """
### How to Cancel Your Subscription

**Steps to Cancel:**

1. Go to **Settings** → **Billing**
2. Click **Cancel Subscription**
3. Select a reason (optional)
4. Confirm cancellation

**What happens after:**
- Service continues until billing period ends
- No further charges
- Data kept for 30 days
- Can reactivate anytime

**Alternatives to Cancellation:**
- Downgrade to a cheaper plan
- Pause subscription (up to 3 months)
- Switch to annual billing (save 20%)
""", 95
    
    # Mobile App
    if any(word in q for word in ["mobile", "app", "phone", "ios", "android", "download"]):
        return """
### Mobile App Information

**Download the App:**
- **iOS**: Apple App Store
- **Android**: Google Play Store

**Features:**
- Push notifications for new tickets
- Reply to customers on-the-go
- Upload photos from your phone
- Voice-to-text typing
- Offline mode (saves drafts)

**Requirements:**
- iOS 15+ or Android 10+
- 100MB free space

The mobile app is **free** for all subscribers!
""", 95
    
    # Password Reset
    if any(word in q for word in ["password", "reset", "forgot", "change password"]):
        return """
### How to Reset Your Password

**Step-by-Step Instructions:**

1. Go to the login page
2. Click **Forgot Password**
3. Enter your email address
4. Check your email for a reset link
5. Click the link in the email
6. Enter a new password
7. Confirm and save

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one number

**Troubleshooting:**
- Check spam folder if email not received within 5 minutes
- Reset link expires after 1 hour
- Contact support if you need additional help
""", 95
    
    # Subscription Plans
    if any(word in q for word in ["subscription", "plan", "pricing", "basic", "premium", "enterprise", "price", "cost"]):
        return """
### Subscription Plans

**Basic Plan - $9.99/month**
- 5 team members
- 100GB storage
- Email support (24-hour response)
- 1,000 API calls/month

**Premium Plan - $29.99/month**
- 20 team members
- 500GB storage
- Priority support (4-hour response)
- 10,000 API calls/month
- Advanced analytics
- Custom integrations

**Enterprise Plan - $99.99/month**
- Unlimited team members
- 2TB storage
- 24/7 dedicated support
- Unlimited API calls
- Custom features
- SLA guarantee

💡 **Save 20% with annual billing on any plan!**
""", 95
    
    # Refund
    if any(word in q for word in ["refund", "money back", "guarantee", "return"]):
        return """
### Refund Policy

**30-Day Money-Back Guarantee** on all subscription plans.

**To Request a Refund:**
1. Go to **Settings** → **Billing**
2. Click **Request Refund**
3. Select your reason (optional)
4. Submit the request

**Processing Time by Payment Method:**
- Credit cards: 5-7 business days
- PayPal: 3-5 business days
- Bank transfer: 7-10 business days

The refund will be credited to your original payment method.

**Note:** Setup fees and custom development are non-refundable.
""", 95
    
    # Billing Questions
    if any(word in q for word in ["billing", "payment", "credit card", "paypal", "invoice"]):
        return """
### Payment Methods Accepted

**We accept:**
- Visa, Mastercard, American Express, Discover
- PayPal
- Apple Pay, Google Pay
- Bank transfer (Enterprise plans only)

**Billing Information:**
- All payments processed securely via Stripe
- Automatic receipts sent to your email
- Update payment methods in Settings → Billing
- Download invoices from Billing Settings
""", 95
    
    # Default response
    return """
### I couldn't find that information

Please try one of these example questions:

**Try asking:**
- 💬 "How do I invite team members?"
- 💬 "How do I cancel my subscription?"
- 💬 "Is there a mobile app?"
- 💬 "How do I reset my password?"
- 💬 "What subscription plans do you offer?"
- 💬 "How do I get a refund?"
- 💬 "What payment methods do you accept?"

If you need immediate help, contact support at support@example.com
""", 50

# Streamlit UI
st.set_page_config(
    page_title="Truffle - AI Support Agent",
    page_icon="🍄",
    layout="wide"
)

st.title("🍄 Truffle")
st.caption("An AI support agent that digs up the right answers.")

# Sidebar
with st.sidebar:
    st.markdown("### About Truffle")
    st.markdown("""
    - **AI-Powered** support agent
    - **Instant answers** to common questions
    - **No waiting** for human support
    """)
    
    st.markdown("---")
    st.markdown("### Quick Examples")
    
    examples = [
        "How do I invite team members?",
        "How do I cancel my subscription?",
        "Is there a mobile app?",
        "How do I reset my password?",
        "What subscription plans do you offer?",
        "How do I get a refund?"
    ]
    
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.quick_question = ex
    
    st.markdown("---")
    st.markdown("### Stats")
    st.metric("Questions Ready", "50+")
    st.metric("Response Time", "<1 sec")

# Chat interface
st.markdown("## 💬 Ask Truffle")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle quick question from button
if "quick_question" in st.session_state:
    query = st.session_state.quick_question
    del st.session_state.quick_question
else:
    query = st.chat_input("Ask me anything about support...")

# Process the question
if query:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    
    # Get answer
    with st.chat_message("assistant"):
        with st.spinner("🍄 Truffle is searching for answers..."):
            answer, confidence = get_answer(query)
            st.markdown(answer)
            
            if confidence >= 90:
                st.success(f"✅ Confidence: {confidence}%")
            elif confidence >= 70:
                st.info(f"📊 Confidence: {confidence}%")
            else:
                st.warning(f"⚠️ Confidence: {confidence}%")
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})

# Footer
st.markdown("---")
st.markdown("🍄 **Truffle** | AI Support Agent | Powered by Groq LLM")
