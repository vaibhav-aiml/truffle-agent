"""Updated team management document with better search keywords."""

from backend.rag.smart_vector_store import SmartVectorStore

store = SmartVectorStore()

# First, remove old team document if exists
store.documents = [doc for doc in store.documents if "team" not in doc["metadata"].get("source", "").lower()]

# Add improved team management document
improved_team_doc = {
    "id": "team_updated_001",
    "source": "team_management_guide.md",
    "category": "account",
    "content": """
    HOW TO INVITE TEAM MEMBERS - STEP BY STEP GUIDE:
    
    To invite team members to your account, follow these steps:
    
    1. Log into your account dashboard
    2. Click on "Settings" in the left sidebar
    3. Select "Team" or "Team Members" from the menu
    4. Click the blue "Invite Member" button
    5. Enter the person's email address
    6. Choose their role: Admin, Member, or Viewer
    7. Click "Send Invitation"
    8. They will receive an email with a join link
    
    Team Member Roles Explained:
    
    Admin Role:
    - Can invite and remove members
    - Full access to all settings
    - Can change subscription
    - View billing information
    
    Member Role:
    - Can create and edit tickets
    - Cannot manage team members
    - Cannot access billing
    
    Viewer Role:
    - Read-only access
    - Cannot make changes
    - Perfect for stakeholders
    
    Team Size Limits by Plan:
    - Basic plan: Maximum 5 team members
    - Premium plan: Maximum 20 team members
    - Enterprise plan: Unlimited team members
    
    Need to invite someone? Go to Settings → Team → Invite Member.
    """
}

store.add_document(improved_team_doc)
print("✅ Added improved team management document")
print(f"Total documents now: {store.count()}")
