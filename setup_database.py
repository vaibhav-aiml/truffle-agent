"""Setup script to initialize and seed the SQLite tickets database."""

import os
import sqlite3
from backend.config import settings
from backend.services.sql_service import ensure_database_exists

def run_database_setup():
    db_path = str(settings.DB_PATH)
    print(f"Initializing database at: {db_path}")
    
    # Reset existing DB for fresh setup
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("  Cleared old database.")
        except Exception as e:
            print(f"  Warning: could not delete old database file: {e}")
            
    ensure_database_exists(db_path)
    
    # Verify records
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tickets")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
        status_counts = cursor.fetchall()
        
        conn.close()
        
        print(f"\n[OK] Database seeded successfully!")
        print(f"  Total Tickets: {count}")
        for status, cnt in status_counts:
            print(f"    - {status}: {cnt}")
    except Exception as e:
        print(f"[Error] Failed to verify seeded data: {e}")

if __name__ == "__main__":
    run_database_setup()
