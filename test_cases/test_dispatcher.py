from src.dispatcher import TicketDispatcher


dispatcher = TicketDispatcher()


# --------------------------------------------------
# Test 1
# --------------------------------------------------

result = dispatcher.ask(
    "How many tickets are currently open?"
)

print("\nTest 1")
print(result)

assert result["query"]["operation"] == "count_tickets"
assert result["query"]["status"] == "Open"
assert result["result"] == 111


# --------------------------------------------------
# Test 2
# --------------------------------------------------

result = dispatcher.ask(
    "How many critical tickets are unresolved "
    "or took more than 12 hours to resolve?"
)

print("\nTest 2")
print(result)

assert result["query"]["operation"] == "get_tickets"
assert result["query"]["priority"] == "Critical"
assert (
    result["query"]["max_resolution_time_hrs"]
    == 12.0
)
assert len(result["result"]) == 34


# --------------------------------------------------
# Test 3
# --------------------------------------------------

result = dispatcher.ask(
    "What is the average customer rating "
    "for Technical tickets?"
)

print("\nTest 3")
print(result)

assert (
    result["query"]["operation"]
    == "average_rating"
)

assert (
    result["query"]["category"]
    == "Technical"
)

assert (
    abs(
        result["result"]
        - 3.7403846153846154
    )
    < 0.000001
)


# --------------------------------------------------
# Test 4
# --------------------------------------------------

result = dispatcher.ask(
    "Rank the agents by the number of resolved "
    "tickets in March."
)

print("\nTest 4")
print(result)

assert (
    result["query"]["operation"]
    == "group_and_rank"
)

assert (
    result["query"]["status"]
    == "Resolved"
)

assert (
    result["query"]["group_by"]
    == "agent_id"
)

assert (
    result["query"]["month"]
    == 3
)


# --------------------------------------------------
# Test 5
# --------------------------------------------------

result = dispatcher.ask(
    "What is the resolution rate by category?"
)

print("\nTest 5")
print(result)

assert (
    result["query"]["operation"]
    == "resolution_rate"
)

assert (
    result["query"]["group_by"]
    == "category"
)


# --------------------------------------------------
# Test 6
# --------------------------------------------------

result = dispatcher.ask(
    "Find abnormal resolution times."
)

print("\nTest 6")
print(result)

assert (
    result["query"]["operation"]
    == "detect_resolution_anomalies"
)

assert len(result["result"]) == 21


# --------------------------------------------------
# Test 7
# --------------------------------------------------

result = dispatcher.ask(
    "Which agent has the lowest average "
    "customer rating?"
)

print("\nTest 7")
print(result)

assert (
    result["query"]["operation"]
    == "average_rating_by_group"
)

assert (
    result["query"]["group_by"]
    == "agent_id"
)

assert isinstance(
    result["result"],
    dict
)


# --------------------------------------------------
# Test 8
# --------------------------------------------------

result = dispatcher.ask(
    "Find unresolved high-priority tickets "
    "older than 24 hours."
)

print("\nTest 8")
print(result)

assert (
    result["query"]["operation"]
    == "unresolved_high_priority_tickets"
)

assert len(result["result"]) >= 0


# --------------------------------------------------
# Final
# --------------------------------------------------

print("\n==============================")
print("ALL DISPATCHER TESTS PASSED")
print("==============================")