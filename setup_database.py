"""Create SQLite database with sample ticket data."""

import sqlite3
from datetime import datetime, timedelta
import random

# Create database
conn = sqlite3.connect("data/processed/sql_db/tickets.db")
cursor = conn.cursor()

# Drop existing table if exists
cursor.execute("DROP TABLE IF EXISTS tickets")

# Create tickets table
cursor.execute("""
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY,
    customer_name TEXT,
    customer_email TEXT,
    subject TEXT,
    description TEXT,
    status TEXT,
    priority TEXT,
    assigned_to TEXT,
    created_at DATE,
    resolved_at DATE,
    satisfaction_score INTEGER
)
""")

# Sample data
customers = [
    ("John Smith", "john@example.com"),
    ("Sarah Johnson", "sarah@example.com"),
    ("Mike Brown", "mike@example.com"),
    ("Lisa Wilson", "lisa@example.com"),
    ("David Lee", "david@example.com"),
    ("Anna Martinez", "anna@example.com"),
    ("James Taylor", "james@example.com"),
]

subjects = [
    "Cannot login to account",
    "Billing issue - incorrect charge",
    "Feature request: dark mode",
    "Bug report: app crashes",
    "Password reset not working",
    "Need help with API integration",
    "Subscription upgrade question",
    "Data export request",
    "Two-factor authentication issue",
    "Slow performance on dashboard"
]

statuses = ["open", "in_progress", "resolved", "closed"]
priorities = ["low", "medium", "high", "urgent"]
agents = ["Alice", "Bob", "Charlie", "Diana", "Eve"]

# Generate 50 sample tickets
tickets = []
for i in range(1, 51):
    customer = random.choice(customers)
    created_date = datetime.now() - timedelta(days=random.randint(0, 30))
    status = random.choice(statuses)
    
    resolved_date = None
    satisfaction = None
    
    if status in ["resolved", "closed"]:
        resolved_date = created_date + timedelta(days=random.randint(1, 7))
        satisfaction = random.randint(1, 5)
    
    ticket = (
        i,
        customer[0],
        customer[1],
        random.choice(subjects),
        f"Customer reported: {random.choice(subjects)}",
        status,
        random.choice(priorities),
        random.choice(agents),
        created_date.strftime("%Y-%m-%d"),
        resolved_date.strftime("%Y-%m-%d") if resolved_date else None,
        satisfaction
    )
    tickets.append(ticket)

# Insert data
cursor.executemany("""
INSERT INTO tickets (
    id, customer_name, customer_email, subject, description, 
    status, priority, assigned_to, created_at, resolved_at, satisfaction_score
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", tickets)

conn.commit()

# Show summary
cursor.execute("SELECT COUNT(*) FROM tickets")
count = cursor.fetchone()[0]

cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
status_counts = cursor.fetchall()

print(f"✅ Database created!")
print(f"📊 Total tickets: {count}")
print(f"\n📈 Tickets by status:")
for status, cnt in status_counts:
    print(f"   - {status}: {cnt}")

conn.close()
print(f"\n📍 Database location: data/processed/sql_db/tickets.db")
