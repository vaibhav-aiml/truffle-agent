"""Utility script to export SQL and RAG fine-tuning datasets in Alpaca and ShareGPT formats."""

import os
import json
import sqlite3
import sys
from pathlib import Path

# Add current directory to path so backend imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config import settings
from backend.services.sql_service import convert_question_to_sql
from backend.services.vector_service import load_vector_db
from backend.evaluation.test_cases import get_all_test_cases

def export_sql_dataset() -> list[dict]:
    """Generate SQL fine-tuning dataset based on templates and evaluation test cases."""
    dataset = []
    
    # Expose tickets schema for the LLM instruction context
    schema_info = "Table schema: tickets (id, customer_name, customer_email, subject, description, status, priority, assigned_to, created_at, resolved_at, satisfaction_score, category)"
    
    # 1. Add SQL test cases from suite
    test_cases = get_all_test_cases()
    for case in test_cases:
        if case["expected_source"] == "sql":
            query = case["query"]
            res = convert_question_to_sql(query)
            if res["sql"]:
                dataset.append({
                    "instruction": f"Write a SQLite query for this natural language question against the tickets table.\n{schema_info}",
                    "input": query,
                    "output": res["sql"]
                })
                
    # 2. Template-based query extensions
    agents = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    for agent in agents:
        dataset.append({
            "instruction": f"Write a SQLite query to list tickets assigned to a specific agent.\n{schema_info}",
            "input": f"Show tickets assigned to {agent}",
            "output": f"SELECT * FROM tickets WHERE UPPER(assigned_to) = UPPER('{agent}') LIMIT 20"
        })
        dataset.append({
            "instruction": f"Write a SQLite query to list tickets assigned to a specific agent.\n{schema_info}",
            "input": f"List tickets for {agent}",
            "output": f"SELECT * FROM tickets WHERE UPPER(assigned_to) = UPPER('{agent}') LIMIT 20"
        })
        
    statuses = ["open", "resolved", "closed", "in_progress"]
    for status in statuses:
        dataset.append({
            "instruction": f"Write a SQLite query to count tickets matching a specific status.\n{schema_info}",
            "input": f"How many {status} tickets do we have?",
            "output": f"SELECT COUNT(*) FROM tickets WHERE status = '{status}'"
        })
        dataset.append({
            "instruction": f"Write a SQLite query to list tickets by status.\n{schema_info}",
            "input": f"Show all {status} tickets",
            "output": f"SELECT * FROM tickets WHERE status = '{status}' LIMIT 20"
        })
        
    return dataset

def export_rag_dataset() -> list[dict]:
    """Generate RAG fine-tuning dataset based on indexed knowledge base articles."""
    dataset = []
    
    # Load document vectors from settings dir
    documents = load_vector_db(str(settings.VECTOR_DB_DIR))
    
    for doc in documents:
        content = doc["content"]
        source = doc["metadata"].get("source", "unknown")
        category = doc["metadata"].get("category", "general")
        
        # General documentation lookup instruction
        dataset.append({
            "instruction": f"Answer the customer support question strictly using the context below. Source: {source}",
            "input": f"Context:\n{content}\n\nQuery: Explain the policy or details outlined in this document.",
            "output": f"This document covers {category} policy. Here are the key details:\n{content}"
        })
        
        # Specific Q&A variations based on matching documentation
        if "payment" in doc["id"]:
            dataset.append({
                "instruction": "Answer the customer query based on the billing context.",
                "input": f"Context:\n{content}\n\nQuery: What payment methods do you accept?",
                "output": "We accept Visa, Mastercard, American Express, Discover, JCB, Diners Club, PayPal, Apple Pay, Google Pay, Samsung Pay, Venmo, and ACH/Wire transfers (Enterprise plans only)."
            })
        elif "password" in doc["id"]:
            dataset.append({
                "instruction": "Answer the customer query based on the account context.",
                "input": f"Context:\n{content}\n\nQuery: How do I reset my password?",
                "output": "1. Go to the login page.\n2. Click 'Forgot Password'.\n3. Enter your email.\n4. Click 'Send Reset Link'.\n5. Check email and click the link.\n6. Enter new password (min 8 chars, 1 uppercase, 1 lowercase, 1 number) and save."
            })
        elif "subscription" in doc["id"]:
            dataset.append({
                "instruction": "Answer the customer query based on the pricing context.",
                "input": f"Context:\n{content}\n\nQuery: What subscription plans do you offer?",
                "output": "We offer:\n- Basic: $9.99/mo (5 members, 100GB storage, email support)\n- Premium: $29.99/mo (20 members, 500GB storage, priority support, annual 20% discount)\n- Enterprise: $99.99/mo (Unlimited members, 2TB storage, 24/7 dedicated support, SLA uptime commitment)"
            })
        elif "refund" in doc["id"]:
            dataset.append({
                "instruction": "Answer the customer query based on the refund policy context.",
                "input": f"Context:\n{content}\n\nQuery: How do I request a refund?",
                "output": "You qualify for a 30-day money-back guarantee. Go to Settings -> Billing, click 'Request Refund', and submit. Processing takes 5-7 business days for cards, 3-5 days for PayPal."
            })
            
    return dataset

def export_all():
    """Consolidate datasets and write json files to output directory."""
    output_dir = settings.BASE_DIR / "data/processed/finetuning"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating fine-tuning datasets...")
    
    sql_data = export_sql_dataset()
    rag_data = export_rag_dataset()
    
    combined_data = sql_data + rag_data
    
    # Write Alpaca format (Instruction/Input/Output)
    alpaca_file = output_dir / "alpaca_finetuning.json"
    with open(alpaca_file, "w") as f:
        json.dump(combined_data, f, indent=2)
        
    # Write ShareGPT format (Conversations)
    sharegpt_file = output_dir / "sharegpt_finetuning.json"
    sharegpt_data = []
    for item in combined_data:
        sharegpt_data.append({
            "conversations": [
                {
                    "from": "human",
                    "value": f"{item['instruction']}\n\nInput:\n{item['input']}"
                },
                {
                    "from": "gpt",
                    "value": item["output"]
                }
            ]
        })
        
    with open(sharegpt_file, "w") as f:
        json.dump(sharegpt_data, f, indent=2)
        
    print(f"\n[OK] Fine-tuning dataset generation complete!")
    print(f"  SQL training samples: {len(sql_data)}")
    print(f"  RAG training samples: {len(rag_data)}")
    print(f"  Total samples exported: {len(combined_data)}")
    print(f"  Alpaca File: {alpaca_file}")
    print(f"  ShareGPT File: {sharegpt_file}")

if __name__ == "__main__":
    export_all()
