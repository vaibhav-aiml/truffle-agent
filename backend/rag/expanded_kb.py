"""Expanded knowledge base for Truffle - 15+ documents."""

EXPANDED_KB = [
    {
        "id": "doc_001",
        "source": "getting_started.md",
        "category": "onboarding",
        "content": """
        GETTING STARTED GUIDE:
        
        Welcome to our platform! Here's how to get started:
        
        1. Create your account using work email
        2. Verify your email address
        3. Set up your profile (name, role, avatar)
        4. Choose your subscription plan
        5. Invite team members
        6. Complete the onboarding tutorial
        
        First 14 days are free on any plan!
        """
    },
    {
        "id": "doc_002",
        "source": "billing_faq.md",
        "category": "billing",
        "content": """
        BILLING FREQUENTLY ASKED QUESTIONS:
        
        Q: When am I billed?
        A: Monthly plans bill on the same date each month. Annual plans bill once per year.
        
        Q: Can I change my billing cycle?
        A: Yes, contact support to switch from monthly to annual.
        
        Q: What happens if payment fails?
        A: We retry for 5 days. After that, account is suspended.
        
        Q: Do you offer discounts for non-profits?
        A: Yes, 40% discount for registered non-profits.
        
        Q: Can I get a VAT invoice?
        A: Yes, download from Billing Settings.
        """
    },
    {
        "id": "doc_003",
        "source": "team_management.md",
        "category": "account",
        "content": """
        TEAM MANAGEMENT GUIDE:
        
        Inviting Team Members:
        - Go to Settings → Team
        - Click "Invite Member"
        - Enter email address
        - Select role (Admin, Member, Viewer)
        - Send invitation
        
        Roles and Permissions:
        - Admin: Full access, can invite/remove members
        - Member: Can create and edit, cannot manage team
        - Viewer: Read-only access
        
        Team Size Limits by Plan:
        - Basic: 5 members
        - Premium: 20 members
        - Enterprise: Unlimited
        """
    },
    {
        "id": "doc_004",
        "source": "security_best_practices.md",
        "category": "security",
        "content": """
        SECURITY BEST PRACTICES:
        
        Account Security:
        - Enable two-factor authentication (2FA)
        - Use strong passwords (12+ characters)
        - Never share login credentials
        - Review active sessions regularly
        
        Data Protection:
        - All data encrypted at rest (AES-256)
        - TLS 1.3 for data in transit
        - Automatic backups every 24 hours
        - SOC 2 Type II certified
        
        If you suspect unauthorized access:
        - Immediately reset password
        - Revoke all API keys
        - Contact security@example.com
        """
    },
    {
        "id": "doc_005",
        "source": "api_authentication.md",
        "category": "developer",
        "content": """
        API AUTHENTICATION GUIDE:
        
        Getting API Access:
        1. Go to Developer Settings
        2. Click "Create API Key"
        3. Name your key (e.g., "Production Server")
        4. Choose permissions (Read, Write, Admin)
        5. Copy and store securely
        
        Using API Keys:
        - Include in header: Authorization: Bearer YOUR_API_KEY
        - Rate limits: 1000 requests/minute for Basic, 10K for Premium
        - Keys never expire but can be revoked
        
        Example Request:
        curl -X GET https://api.example.com/v1/users \
          -H "Authorization: Bearer YOUR_API_KEY"
        """
    },
    {
        "id": "doc_006",
        "source": "data_export.md",
        "category": "account",
        "content": """
        DATA EXPORT GUIDE:
        
        You can export your data anytime:
        
        Supported Formats:
        - CSV (spreadsheet format)
        - JSON (developer format)
        - PDF (report format)
        
        What Can Be Exported:
        - All tickets and conversations
        - User activity logs
        - Analytics data
        - Billing history
        
        Export Process:
        1. Go to Settings → Data
        2. Select data type
        3. Choose date range
        4. Select format
        5. Click "Export"
        6. Download link sent to email
        
        Enterprise plans get real-time API access to all data.
        """
    },
    {
        "id": "doc_007",
        "source": "integrations.md",
        "category": "product",
        "content": """
        AVAILABLE INTEGRATIONS:
        
        Native Integrations:
        - Slack: Get notifications in channels
        - Microsoft Teams: Sync tickets
        - Zapier: Connect 5000+ apps
        - Salesforce: Sync customer data
        - HubSpot: Track support tickets
        - Jira: Link bug reports
        
        Custom Integrations:
        - Webhooks for real-time events
        - REST API for custom apps
        - Zapier for no-code automation
        
        Setting Up Slack Integration:
        1. Go to Integrations → Slack
        2. Click "Connect Workspace"
        3. Authorize access
        4. Choose notification channel
        5. Save settings
        """
    },
    {
        "id": "doc_008",
        "source": "ticket_workflow.md",
        "category": "automation",
        "content": """
        AUTOMATED TICKET WORKFLOWS:
        
        Automatic Assignment:
        - Round-robin to available agents
        - Assign by expertise (billing, tech, general)
        - Priority-based routing
        
        Auto-Responses:
        - Acknowledge receipt immediately
        - Send knowledge base articles
        - Collect missing information
        
        Escalation Rules:
        - Unassigned after 1 hour → Team lead
        - No response after 4 hours → Manager
        - High priority → Immediate alert
        
        SLA Tracking:
        - First response: 2 hours (Premium), 30 min (Enterprise)
        - Resolution time: 24 hours (Premium), 4 hours (Enterprise)
        - Critical issues: 1 hour response
        """
    },
    {
        "id": "doc_009",
        "source": "mobile_app.md",
        "category": "product",
        "content": """
        MOBILE APP GUIDE:
        
        Download from:
        - iOS: Apple App Store
        - Android: Google Play Store
        
        Mobile Features:
        - Push notifications for new tickets
        - Reply to customers on-the-go
        - Attach photos from phone
        - Voice-to-text for quick replies
        - Offline mode (saves drafts)
        
        System Requirements:
        - iOS 15+ or Android 10+
        - 100MB free space
        - Internet connection
        
        Coming Soon:
        - Face ID / Fingerprint login
        - Voice commands
        - Real-time analytics dashboard
        """
    },
    {
        "id": "doc_010",
        "source": "downtime_policy.md",
        "category": "support",
        "content": """
        SERVICE UPTIME & DOWNTIME POLICY:
        
        Uptime Guarantees by Plan:
        - Basic: 99.5% uptime
        - Premium: 99.9% uptime
        - Enterprise: 99.99% uptime with SLA credits
        
        Scheduled Maintenance:
        - Notified 7 days in advance
        - Performed during off-hours (2-4 AM)
        - Maximum 4 hours per month
        
        Unscheduled Downtime:
        - Status page updates every 15 minutes
        - Email notifications to admins
        - Post-incident report within 24 hours
        
        SLA Credits (Enterprise):
        - 99.9-99.99% uptime → 10% credit
        - 99.0-99.89% uptime → 25% credit
        - Below 99% → 50% credit
        """
    },
    {
        "id": "doc_011",
        "source": "training_resources.md",
        "category": "education",
        "content": """
        TRAINING & RESOURCES:
        
        Free Resources:
        - Video tutorials (Getting Started, Advanced Features)
        - Knowledge base with 200+ articles
        - Webinars every Tuesday
        - Community forum with 10k+ members
        
        Paid Training:
        - Admin certification ($499)
        - Developer course ($799)
        - Team training (custom pricing)
        
        Documentation:
        - API reference docs
        - Integration guides
        - Best practices
        - Troubleshooting guides
        
        Office Hours:
        - Free 30-min sessions every Thursday
        - Book through support dashboard
        - Ask questions about your use case
        """
    },
    {
        "id": "doc_012",
        "source": "cancellation_process.md",
        "category": "billing",
        "content": """
        CANCELLATION PROCESS:
        
        How to Cancel:
        1. Go to Settings → Billing
        2. Click "Cancel Subscription"
        3. Select reason for cancellation
        4. Confirm cancellation
        5. Service continues until billing period ends
        
        What Happens After Cancellation:
        - Data retained for 30 days
        - Can reactivate anytime during retention
        - After 30 days, data is permanently deleted
        - No refunds for partial months
        
        Alternatives to Cancellation:
        - Downgrade to lower plan (saves money)
        - Pause subscription (freeze for 3 months)
        - Switch to annual billing (20% savings)
        
        Need Help?
        Contact retention specialist for custom offers.
        """
    }
]

def get_expanded_kb():
    return EXPANDED_KB

def get_kb_by_category(category):
    return [doc for doc in EXPANDED_KB if doc.get("category") == category]

def get_kb_by_source(source):
    return [doc for doc in EXPANDED_KB if doc.get("source") == source]

if __name__ == "__main__":
    print(f"📚 Loaded {len(EXPANDED_KB)} documents")
    categories = set(doc["category"] for doc in EXPANDED_KB)
    print(f"📂 Categories: {', '.join(categories)}")
