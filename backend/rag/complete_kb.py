"""Complete knowledge base for Truffle."""

COMPLETE_KNOWLEDGE_BASE = [
    {
        "id": "kb_001",
        "source": "payment_methods.md",
        "category": "billing",
        "content": """
PAYMENT METHODS ACCEPTED:

We accept these payment methods:
- Visa, Mastercard, American Express, Discover
- PayPal
- Apple Pay and Google Pay
- Bank transfer (Enterprise plans only)

All payments are processed securely via Stripe.
You can update payment methods in Settings > Billing.
"""
    },
    {
        "id": "kb_002", 
        "source": "password_reset.md",
        "category": "account",
        "content": """
PASSWORD RESET STEPS:

1. Click 'Forgot Password' on the login page
2. Enter your email address
3. Check your email for a reset link
4. Click the link and create a new password
5. Password must be at least 8 characters

If you don't see the email, check your spam folder.
"""
    },
    {
        "id": "kb_003",
        "source": "subscription_plans.md", 
        "category": "billing",
        "content": """
SUBSCRIPTION PLANS:

Basic Plan: $9.99/month - 5 team members, 100GB storage
Premium Plan: $29.99/month - 20 team members, 500GB storage  
Enterprise Plan: $99.99/month - Unlimited team members, 2TB storage

Save 20% with annual billing.
"""
    },
    {
        "id": "kb_004",
        "source": "refund_policy.md",
        "category": "billing", 
        "content": """
REFUND POLICY:

30-day money-back guarantee on all plans.
Request refund in Settings > Billing.
Refunds take 5-7 business days.
"""
    }
]

def get_knowledge_base():
    return COMPLETE_KNOWLEDGE_BASE
