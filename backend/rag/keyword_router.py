"""Keyword-based router for Truffle - Direct matching."""

class KeywordRouter:
    """Routes questions to correct answers using keywords."""
    
    def __init__(self):
        self.rules = [
            {
                "keywords": ["invite", "inviting", "add member", "team member", "add person", "new member", "add someone"],
                "answer": """
HOW TO INVITE TEAM MEMBERS:

Step 1: Log into your account dashboard
Step 2: Click "Settings" in the sidebar
Step 3: Select "Team" or "Team Members"
Step 4: Click the "Invite Member" button
Step 5: Enter the person's email address
Step 6: Choose role (Admin, Member, or Viewer)
Step 7: Click "Send Invitation"

The person will receive an email with a join link.

Role Permissions:
- Admin: Full access, can invite/remove members
- Member: Can create/edit tickets, cannot manage team
- Viewer: Read-only access

Team Limits by Plan:
- Basic: 5 members
- Premium: 20 members  
- Enterprise: Unlimited
""",
                "source": "Team Management Guide"
            },
            {
                "keywords": ["cancel", "cancellation", "unsubscribe", "stop billing", "end subscription"],
                "answer": """
HOW TO CANCEL YOUR SUBSCRIPTION:

Step 1: Go to Settings → Billing
Step 2: Click "Cancel Subscription"
Step 3: Select a reason (optional)
Step 4: Confirm cancellation

What happens after:
- Service continues until billing period ends
- No further charges
- Data kept for 30 days
- Can reactivate anytime

Alternatives to Cancellation:
- Downgrade to a cheaper plan
- Pause subscription (up to 3 months)
- Switch to annual billing (save 20%)
""",
                "source": "Cancellation Guide"
            },
            {
                "keywords": ["mobile app", "phone app", "ios app", "android app", "download app"],
                "answer": """
MOBILE APP INFORMATION:

Download from:
- iOS: Apple App Store
- Android: Google Play Store

Features:
- Push notifications for new tickets
- Reply to customers on-the-go
- Upload photos from phone
- Voice-to-text typing
- Offline mode (saves drafts)

Requirements:
- iOS 15+ or Android 10+
- 100MB free space

The mobile app is free for all subscribers!
""",
                "source": "Mobile App Guide"
            },
            {
                "keywords": ["password", "reset password", "forgot password"],
                "answer": """
HOW TO RESET YOUR PASSWORD:

Step 1: Go to login page
Step 2: Click "Forgot Password"
Step 3: Enter your email address
Step 4: Check your email for reset link
Step 5: Click the link
Step 6: Enter new password
Step 7: Confirm and save

Password Requirements:
- Minimum 8 characters
- One uppercase letter
- One number

If you don't receive the email, check your spam folder.
""",
                "source": "Password Reset Guide"
            },
            {
                "keywords": ["refund", "money back", "get refund"],
                "answer": """
REFUND POLICY:

30-day money-back guarantee on all plans.

To request a refund:
1. Go to Settings → Billing
2. Click "Request Refund"
3. Submit the request

Refunds take 5-7 business days to process.
The refund goes back to your original payment method.
""",
                "source": "Refund Policy"
            },
            {
                "keywords": ["subscription", "plans", "pricing", "basic", "premium", "enterprise"],
                "answer": """
SUBSCRIPTION PLANS:

Basic Plan - $9.99/month:
- 5 team members
- 100GB storage
- Email support

Premium Plan - $29.99/month:
- 20 team members
- 500GB storage
- Priority support
- Advanced analytics

Enterprise Plan - $99.99/month:
- Unlimited team members
- 2TB storage
- 24/7 dedicated support
- Custom features

Save 20% with annual billing!
""",
                "source": "Subscription Plans"
            }
        ]
    
    def route(self, query: str) -> dict:
        """Find matching rule for the query."""
        query_lower = query.lower()
        
        for rule in self.rules:
            for keyword in rule["keywords"]:
                if keyword in query_lower:
                    return {
                        "response": rule["answer"],
                        "source": rule["source"],
                        "confidence": 0.95
                    }
        
        # Default response
        return {
            "response": "I'm not sure about that. Please contact support for help.",
            "source": "Default",
            "confidence": 0.3
        }

if __name__ == "__main__":
    router = KeywordRouter()
    
    test_queries = [
        "How do I invite team members?",
        "How do I cancel my subscription?",
        "Is there a mobile app?",
        "How do I reset my password?"
    ]
    
    for q in test_queries:
        result = router.route(q)
        print(f"\nQ: {q}")
        print(f"A: {result['response'][:100]}...")
        print(f"Confidence: {result['confidence']:.0%}")
