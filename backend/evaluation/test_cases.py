"""Test cases for Truffle evaluation."""

TEST_CASES = [
    {
        "id": 1,
        "query": "How do I reset my password?",
        "expected_source": "knowledge_base",
        "expected_answer_contains": ["password", "reset"],
        "difficulty": "easy",
        "category": "account"
    },
    {
        "id": 2,
        "query": "What subscription plans do you offer?",
        "expected_source": "knowledge_base",
        "expected_answer_contains": ["basic", "premium", "enterprise"],
        "difficulty": "easy",
        "category": "billing"
    },
    {
        "id": 3,
        "query": "How do I get a refund?",
        "expected_source": "knowledge_base",
        "expected_answer_contains": ["refund", "days", "money back"],
        "difficulty": "easy",
        "category": "billing"
    },
    {
        "id": 4,
        "query": "How many open tickets do we have?",
        "expected_source": "sql",
        "expected_sql_pattern": "SELECT COUNT.*FROM tickets",
        "difficulty": "easy",
        "category": "analytics"
    },
    {
        "id": 5,
        "query": "How do I invite team members?",
        "expected_source": "knowledge_base",
        "expected_answer_contains": ["invite", "team", "member"],
        "difficulty": "easy",
        "category": "account"
    },
]

def get_all_test_cases():
    """Return all test cases."""
    return TEST_CASES

def get_test_cases_by_source(source):
    """Filter test cases by expected source."""
    return [tc for tc in TEST_CASES if tc.get("expected_source") == source]

def get_test_cases_by_category(category):
    """Filter test cases by category."""
    return [tc for tc in TEST_CASES if tc.get("category") == category]

def get_test_cases_by_difficulty(difficulty):
    """Filter test cases by difficulty."""
    return [tc for tc in TEST_CASES if tc.get("difficulty") == difficulty]

if __name__ == "__main__":
    tests = get_all_test_cases()
    print(f"✅ Loaded {len(tests)} test cases")
    print(f"   - Knowledge base: {len(get_test_cases_by_source('knowledge_base'))}")
    print(f"   - SQL queries: {len(get_test_cases_by_source('sql'))}")
