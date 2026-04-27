"""Simple test for Truffle - Run this from truffle-agent folder."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

# Import directly
try:
    from backend.text_to_sql.converter import TextToSQL
    print("✅ TextToSQL imported successfully")
    
    t2sql = TextToSQL()
    result = t2sql.answer("How many open tickets?")
    print(f"Result: {result['answer']}")
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying alternative import...")
    
    # Alternative: add parent directory
    parent = os.path.dirname(os.getcwd())
    sys.path.insert(0, parent)
    from backend.text_to_sql.converter import TextToSQL
    print("✅ Imported using parent directory")
