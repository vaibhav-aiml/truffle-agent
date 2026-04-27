"""Simple benchmark script for Truffle."""

import sys
sys.path.append(".")

from backend.evaluation.test_cases import get_all_test_cases

def main():
    print("🍄 Running Truffle Benchmark...")
    print("-" * 40)
    
    test_cases = get_all_test_cases()
    print(f"📊 Loaded {len(test_cases)} test cases")
    
    # Count by source
    kb_count = len([t for t in test_cases if t.get("expected_source") == "knowledge_base"])
    sql_count = len([t for t in test_cases if t.get("expected_source") == "sql"])
    
    print(f"   - Knowledge base queries: {kb_count}")
    print(f"   - Text-to-SQL queries: {sql_count}")
    
    print("\n✅ Benchmark framework ready!")
    print("📝 Add your OpenAI API key to run actual evaluations")

if __name__ == "__main__":
    main()
