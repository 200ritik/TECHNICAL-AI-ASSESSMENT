from src.llm import TicketLLM


llm = TicketLLM()


# Test 1
result = llm.understand_query(
    "How many tickets are currently open?"
)

print("\nTest 1")
print(result)

assert result["operation"] == "count_tickets"
assert result["status"] == "Open"


# Test 2
result = llm.understand_query(
    "Show me all critical tickets not resolved within 12 hours."
)

print("\nTest 2")
print(result)

assert result["operation"] == "get_tickets"
assert result["priority"] == "Critical"
assert result["max_resolution_time_hrs"] == "12"


# Test 3
result = llm.understand_query(
    "What is the average customer rating for Technical tickets?"
)

print("\nTest 3")
print(result)

assert result["operation"] == "average_rating"
assert result["category"] == "Technical"


# Test 4
result = llm.understand_query(
    "Which agent resolved the most tickets in March?"
)

print("\nTest 4")
print(result)

assert result["operation"] == "group_and_rank"
assert result["group_by"] == "agent_id"
assert result["status"] == "Resolved"
assert result["month"] == 3


# Test 5
result = llm.understand_query(
    "Which category has the highest resolution rate?"
)

print("\nTest 5")
print(result)

assert result["operation"] == "resolution_rate"
assert result["group_by"] == "category"


# Test 6
result = llm.understand_query(
    "Are there any anomalies in resolution times?"
)

print("\nTest 6")
print(result)

assert result["operation"] == "detect_resolution_anomalies"


print("\n==============================")
print("ALL TESTS PASSED")
print("==============================")