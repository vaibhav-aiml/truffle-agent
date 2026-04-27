"""Reset and rebuild Truffle knowledge base."""

import shutil
from pathlib import Path

# Clear old data
vectors_file = Path("data/processed/embeddings/vectors.json")
if vectors_file.exists():
    vectors_file.unlink()
    print("Deleted vectors.json")

chunks_dir = Path("data/processed/chunks")
if chunks_dir.exists():
    shutil.rmtree(chunks_dir)
    print("Cleared chunks directory")

# Recreate directories
chunks_dir.mkdir(parents=True, exist_ok=True)
Path("data/processed/embeddings").mkdir(parents=True, exist_ok=True)

print("\n✅ Cleanup complete!")

# Now rebuild
from backend.rag.vector_store import SimpleVectorStore

print("\n📚 Loading knowledge base...")
store = SimpleVectorStore()

# Add documents directly
docs_to_add = [
    {
        "id": "payment_001",
        "source": "payment_methods.md",
        "category": "billing",
        "content": """
PAYMENT METHODS ACCEPTED:

We accept these payment methods:
- Credit Cards: Visa, Mastercard, American Express, Discover
- Digital Payments: PayPal, Apple Pay, Google Pay
- Bank Transfer (for Enterprise plans only)

All payments are processed securely via Stripe.
You can update payment methods in Settings > Billing.
"""
    },
    {
        "id": "password_001",
        "source": "password_reset.md",
        "category": "account",
        "content": """
PASSWORD RESET STEPS:

1. Click 'Forgot Password' on the login page
2. Enter your email address
3. Check your email for a reset link (check spam folder if not received)
4. Click the link and create a new password
5. Password must be at least 8 characters with one uppercase letter and number
"""
    },
    {
        "id": "subscription_001",
        "source": "subscription_plans.md",
        "category": "billing",
        "content": """
SUBSCRIPTION PLANS:

Basic Plan: $9.99/month
- 5 team members
- 100GB storage
- Email support

Premium Plan: $29.99/month
- 20 team members
- 500GB storage
- Priority support
- Advanced analytics

Enterprise Plan: $99.99/month
- Unlimited team members
- 2TB storage
- 24/7 dedicated support
- Custom features

Save 20% with annual billing on any plan.
"""
    },
    {
        "id": "refund_001",
        "source": "refund_policy.md",
        "category": "billing",
        "content": """
REFUND POLICY:

30-day money-back guarantee on all subscription plans.

To request a refund:
1. Go to Settings → Billing
2. Click "Request Refund"
3. Submit the request

Refunds are processed within 5-7 business days.
The refund will be credited to your original payment method.
"""
    }
]

for doc in docs_to_add:
    store.add_document(doc)
    print(f"  Added: {doc['source']}")

print(f"\n✅ Indexed {store.count()} documents!")
print("\nDocuments in store:")
for i, doc in enumerate(store.documents):
    source = doc['metadata'].get('source', 'unknown')
    print(f"  {i+1}. {doc['id']} - {source}")
