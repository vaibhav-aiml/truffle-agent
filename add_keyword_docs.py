"""Add documents with multiple keyword variations."""

from backend.rag.smart_vector_store import SmartVectorStore

store = SmartVectorStore()

# Document with multiple ways to ask the same question
keyword_docs = [
    {
        "id": "invite_keywords_001",
        "source": "how_to_invite_people.md",
        "category": "account",
        "content": """
        INVITING PEOPLE TO YOUR ACCOUNT - KEYWORD GUIDE:
        
        This document helps answer questions about:
        - Inviting team members
        - Adding colleagues
        - Adding new users
        - How to add someone to my account
        - Invite people to join
        - Add team members
        - Send invitation to coworker
        - How do I add a new person
        - Invitation process
        - Adding team members to my organization
        
        STEPS TO INVITE:
        1. Go to Settings
        2. Click Team
        3. Click Invite Member
        4. Enter email address
        5. Choose role (Admin/Member/Viewer)
        6. Send invitation
        
        The invited person receives an email with a link to join.
        """
    },
    {
        "id": "cancel_keywords_001",
        "source": "how_to_cancel_subscription.md",
        "category": "billing",
        "content": """
        CANCELLING YOUR SUBSCRIPTION - COMPLETE GUIDE:
        
        Questions this answers:
        - How do I cancel my subscription?
        - Cancel my plan
        - Stop billing
        - How to unsubscribe
        - End my subscription
        - Turn off auto-renewal
        - How do I stop paying
        
        CANCELLATION STEPS:
        1. Go to Settings → Billing
        2. Click "Cancel Subscription"
        3. Select a reason from the dropdown
        4. Confirm cancellation
        5. Service continues until billing period ends
        
        WHAT HAPPENS AFTER:
        - No further charges
        - Data kept for 30 days
        - Can reactivate anytime
        - After 30 days, data deleted
        
        ALTERNATIVES TO CANCELLATION:
        - Downgrade to cheaper plan
        - Pause subscription for up to 3 months
        - Switch to annual billing for discount
        """
    },
    {
        "id": "mobile_keywords_001",
        "source": "mobile_app_info.md",
        "category": "product",
        "content": """
        MOBILE APP INFORMATION:
        
        Questions this answers:
        - Is there a mobile app?
        - Do you have an app?
        - Can I use on my phone?
        - iOS app available?
        - Android app download
        - Mobile access
        - Phone app
        
        MOBILE APP DETAILS:
        
        Download from:
        - iOS: Apple App Store
        - Android: Google Play Store
        
        Features:
        - Push notifications
        - Reply to tickets
        - Upload photos
        - Voice-to-text typing
        - Offline mode
        
        Requirements:
        - iOS 15+ or Android 10+
        - 100MB free space
        
        The mobile app is free for all subscribers.
        """
    }
]

for doc in keyword_docs:
    store.add_document(doc)
    print(f"✅ Added: {doc['source']}")

print(f"\n📊 Total documents: {store.count()}")
