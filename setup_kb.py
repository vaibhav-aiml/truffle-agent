"""Setup script to index knowledge base documents into the vector database."""

import os
from pathlib import Path
from backend.config import settings
from backend.services.vector_service import add_document_to_db, create_openai_client, save_vector_db

def run_knowledge_base_setup():
    storage_path = str(settings.VECTOR_DB_DIR)
    vectors_file = Path(storage_path) / "vectors.json"
    
    print(f"Initializing knowledge base at: {storage_path}")
    
    if vectors_file.exists():
        try:
            vectors_file.unlink()
            print("  Cleared old vector embeddings file.")
        except Exception as e:
            print(f"  Warning: could not delete old vector database file: {e}")
            
    openai_client = create_openai_client()
    documents = []
    
    # Detailed documents list
    kb_documents = [
        {
            "id": "payment_001",
            "source": "payment_methods.md",
            "category": "billing",
            "content": """
PAYMENT METHODS ACCEPTED - COMPLETE LIST:

We accept the following payment methods:

Credit and Debit Cards:
• Visa (all types)
• Mastercard (all types)
• American Express (Amex)
• Discover Card
• JCB
• Diners Club

Digital Wallets:
• PayPal
• Apple Pay
• Google Pay
• Samsung Pay
• Venmo

Bank Transfers:
• ACH Transfer (US only)
• Wire Transfer (international)
• Direct Debit (European banks)

Enterprise Plans Only:
• Purchase Order (PO)
• Net 30 terms
• Invoice billing

Important Notes:
- All payments are processed securely via Stripe
- We do not store full credit card details
- 3D Secure verification for card payments
- Automatic receipts sent to registered email
- Update payment methods anytime in Settings → Billing

Not Accepted:
• Cryptocurrency (Bitcoin, Ethereum, etc.)
• Cash or checks by mail
• Gift cards
"""
        },
        {
            "id": "subscription_001",
            "source": "subscription_plans.md",
            "category": "billing",
            "content": """
SUBSCRIPTION PLANS - COMPLETE DETAILS:

BASIC PLAN - $9.99 USD per month:
Features:
• 5 team members maximum
• 100 GB storage space
• Email support only (24-hour response)
• 1,000 API calls per month
• Basic analytics dashboard
• Community forum access
• Monthly billing only
• No annual discount

PREMIUM PLAN - $29.99 USD per month:
Features:
• 20 team members maximum
• 500 GB storage space
• Priority email + chat support (4-hour response)
• 10,000 API calls per month
• Advanced analytics with custom reports
• Custom integrations available
• Monthly or annual billing
• 20% discount with annual billing ($287.90/year)

ENTERPRISE PLAN - $99.99 USD per month:
Features:
• Unlimited team members
• 2 TB (2048 GB) storage space
• 24/7 dedicated phone, email, and chat support
• Unlimited API calls
• Custom analytics and AI features
• Custom integrations and SSO
• Monthly or annual billing
• SLA guarantee (99.9% uptime commitment)
• Dedicated account manager
• Onboarding training included

Annual Billing Discount:
Save 20% on any plan when paying annually.
Example: Premium monthly ($29.99) vs annual ($287.90 = $23.99/month)
"""
        },
        {
            "id": "password_001",
            "source": "password_reset.md",
            "category": "account",
            "content": """
PASSWORD RESET - COMPLETE GUIDE:

Step-by-Step Instructions:

Step 1: Go to the login page (app.yourdomain.com)
Step 2: Click the "Forgot Password" link below the login button
Step 3: Enter your registered email address
Step 4: Click the "Send Reset Link" button
Step 5: Check your email inbox (allow 2-3 minutes)
Step 6: Click the password reset link in the email
Step 7: Enter your new password
Step 8: Confirm your new password
Step 9: Click "Reset Password"
Step 10: Log in with your new password

Password Requirements:
• Minimum 8 characters
• At least one uppercase letter (A-Z)
• At least one lowercase letter (a-z)
• At least one number (0-9)
• Special characters are optional but recommended

Troubleshooting:
• Check spam/junk folder if email not received within 5 minutes
• Reset link expires after 1 hour for security
• Request a new link if expired
• Contact support if you need additional help
• Make sure you're using the correct email address
"""
        },
        {
            "id": "refund_001",
            "source": "refund_policy.md",
            "category": "billing",
            "content": """
REFUND POLICY - COMPLETE DETAILS:

30-Day Money-Back Guarantee:
We offer a full 30-day money-back guarantee on all subscription plans.

Eligibility:
• Any subscription plan qualifies
• Must request within 30 days of first payment
• Applies to first subscription only
• No questions asked refund policy

How to Request a Refund:
1. Log into your account dashboard
2. Navigate to Settings → Billing
3. Click on "Request Refund" button
4. Select your reason from the dropdown (optional)
5. Submit the request
6. Confirmation email sent immediately

Processing Times by Payment Method:
• Credit cards: 5-7 business days
• PayPal: 3-5 business days
• Bank transfers: 7-10 business days
• Apple/Google Pay: 5-7 business days

What Gets Refunded:
• Full subscription amount for current month
• No partial refunds for partial months
• Annual plans: prorated refund for unused months
• Setup fees: non-refundable
• Custom development: non-refundable

After Refund:
• Account downgraded to free tier
• Data retained for 30 days
• Can reactivate anytime
"""
        }
    ]
    
    print("  Creating vector embeddings for documents...")
    for doc in kb_documents:
        print(f"    - Embedding: {doc['source']}")
        documents = add_document_to_db(
            openai_client, 
            documents, 
            doc_id=doc["id"], 
            content=doc["content"], 
            source=doc["source"], 
            category=doc["category"]
        )
        
    save_vector_db(storage_path, documents)
    print(f"\n[OK] Knowledge base setup complete! Indexed {len(documents)} documents.")

if __name__ == "__main__":
    run_knowledge_base_setup()
