"""Dynamic performance and accuracy metric computations using functional orchestrator."""

import time
import re
from backend.agents.truffle_agent import create_agent_context, chat_with_agent
from backend.evaluation.test_cases import get_all_test_cases
from backend.utils.logger import logger

def calculate_exact_sql_match(generated_sql: str, expected_pattern: str) -> bool:
    """Check if the generated SQL query matches the expected regex pattern."""
    if not generated_sql or not expected_pattern:
        return False
    try:
        match = re.search(expected_pattern, generated_sql, re.IGNORECASE)
        return bool(match)
    except Exception as e:
        logger.error(f"Error matching regex pattern '{expected_pattern}' in SQL '{generated_sql}': {e}")
        return False

def calculate_rag_accuracy(generated_answer: str, expected_contains: list) -> float:
    """Calculate the ratio of expected keywords present in the generated answer."""
    if not expected_contains:
        return 1.0
    if not generated_answer:
        return 0.0
        
    matched = 0
    generated_lower = generated_answer.lower()
    for word in expected_contains:
        if word.lower() in generated_lower:
            matched += 1
            
    return matched / len(expected_contains)

def run_suite_evaluation() -> dict:
    """Run dynamic agent evaluations against defined test cases using functional contexts."""
    logger.info("Initializing system metric evaluation suite...")
    
    try:
        # Generate stateless agent context
        context = create_agent_context()
    except Exception as e:
        logger.error(f"Failed to initialize functional agent context in metrics: {e}", exc_info=True)
        return {
            "accuracy": 0.0,
            "avg_response_time": 0.0,
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "results": [],
            "error": "Failed to initialize agent context"
        }
        
    test_cases = get_all_test_cases()
    results = []
    total_time = 0.0
    passed_cases = 0
    
    for case in test_cases:
        query = case["query"]
        expected_src = case["expected_source"]
        
        start = time.perf_counter()
        try:
            # Query the stateless chat function
            response_data = chat_with_agent(context, query)
            success = True
        except Exception as e:
            logger.error(f"Exception processing query '{query}': {e}", exc_info=True)
            response_data = {"response": "Error occurred", "type": "error", "sql": None}
            success = False
            
        elapsed = time.perf_counter() - start
        total_time += elapsed
        
        passed = False
        details = ""
        source_type = response_data.get("type")
        
        if success:
            if expected_src == "sql" and source_type == "sql":
                sql_query = response_data.get("sql", "")
                pattern = case.get("expected_sql_pattern", "")
                if calculate_exact_sql_match(sql_query, pattern):
                    passed = True
                    details = "SQL matched expected pattern."
                else:
                    details = f"SQL mismatch. Query: {sql_query} | Pattern: {pattern}"
            elif expected_src == "knowledge_base" and source_type == "rag":
                contains = case.get("expected_answer_contains", [])
                acc = calculate_rag_accuracy(response_data.get("response", ""), contains)
                if acc >= 0.6:  # 60% keyword match counts as success
                    passed = True
                    details = f"RAG keyword matching: {acc*100:.0f}%"
                else:
                    details = f"RAG keyword mismatch. Contains: {contains}"
            else:
                details = f"Route mismatch. Expected: {expected_src}, Got: {source_type}"
        else:
            details = "Evaluation run failed with execution exception."
            
        if passed:
            passed_cases += 1
            
        results.append({
            "id": case["id"],
            "query": query,
            "expected_source": expected_src,
            "actual_source": source_type,
            "passed": passed,
            "latency": elapsed,
            "details": details
        })
        
    avg_latency = total_time / len(test_cases) if test_cases else 0.0
    accuracy = (passed_cases / len(test_cases) * 100) if test_cases else 100.0
    
    logger.info(f"Evaluation complete. Accuracy: {accuracy:.1f}% | Avg Latency: {avg_latency:.2f}s")
    
    return {
        "accuracy": accuracy,
        "avg_response_time": avg_latency,
        "total_cases": len(test_cases),
        "passed_cases": passed_cases,
        "failed_cases": len(test_cases) - passed_cases,
        "results": results
    }

if __name__ == "__main__":
    metrics = run_suite_evaluation()
    print("="*60)
    print(f"Accuracy: {metrics['accuracy']:.1f}%")
    print(f"Avg Response Time: {metrics['avg_response_time']:.2f}s")
    print(f"Passed: {metrics['passed_cases']}/{metrics['total_cases']}")
    print("="*60)
