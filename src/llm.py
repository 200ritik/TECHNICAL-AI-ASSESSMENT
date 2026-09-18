import os
import json

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class TicketLLM:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in .env file."
            )

        self.client = Groq(
            api_key=api_key
        )

        self.model = "openai/gpt-oss-20b"

    def understand_query(self, question):

        system_prompt = """
You are a natural-language query parser for a
customer support ticket dataset.

Your ONLY job is to convert the user's question
into a structured JSON query.

DO NOT answer the user's question.

DO NOT calculate anything.

DO NOT invent information.

The Python query engine will execute the
structured query against the actual dataset.


AVAILABLE OPERATIONS
--------------------

1. count_tickets
2. get_tickets
3. average_rating
4. average_rating_by_group
5. group_and_rank
6. resolution_rate
7. detect_resolution_anomalies
8. unresolved_high_priority_tickets
9. unsupported


count_tickets
-------------

Use ONLY when the user asks for a count based on:

- status
- priority
- category

AND there is NO resolution-time condition.

Examples:

"How many tickets are currently open?"

→ count_tickets
→ status = Open


"How many Critical tickets are there?"

→ count_tickets
→ priority = Critical


"How many Technical tickets are there?"

→ count_tickets
→ category = Technical


IMPORTANT:

If the question contains ANY resolution-time
condition, DO NOT use count_tickets.

Resolution-time conditions include:

- unresolved
- not resolved
- resolved within X hours
- took more than X hours
- older than X hours
- longer than X hours
- resolution time
- unresolved OR took more than X hours


get_tickets
-----------

Use when the question asks to show, list, find,
OR COUNT tickets involving a resolution-time
condition.

This includes:

- unresolved tickets
- tickets not resolved within X hours
- tickets taking more than X hours
- tickets with resolution time greater than X
- tickets that are unresolved OR took more than X hours


An unresolved ticket means:

resolution_time_hrs is null.


IMPORTANT EXAMPLES:

"How many critical tickets are unresolved?"

→ get_tickets
→ priority = Critical
→ max_resolution_time_hrs = "0"


"How many critical tickets took more than 12 hours
to resolve?"

→ get_tickets
→ priority = Critical
→ max_resolution_time_hrs = "12"


"How many critical tickets are unresolved or took
more than 12 hours to resolve?"

→ get_tickets
→ priority = Critical
→ max_resolution_time_hrs = "12"


"Show me all Critical tickets not resolved
within 12 hours."

→ get_tickets
→ priority = Critical
→ max_resolution_time_hrs = "12"


"Show Critical tickets that took more than
24 hours."

→ get_tickets
→ priority = Critical
→ max_resolution_time_hrs = "24"


average_rating
--------------

Use for overall or category-specific
average customer rating.

Example:

"What is the average customer rating for
Technical tickets?"

→ average_rating
→ category = Technical


average_rating_by_group
-----------------------

Use when the user asks for average customer
ratings grouped by agent, category, priority,
or status.

Example:

"Which agent has the lowest average
customer rating?"

→ average_rating_by_group
→ group_by = agent_id


"Which category has the highest average
customer rating?"

→ average_rating_by_group
→ group_by = category


group_and_rank
--------------

Use when the user asks to rank or count
tickets by a group.

Examples:

"Which agent resolved the most tickets?"

→ group_and_rank
→ group_by = agent_id
→ status = Resolved


"Which agent resolved the most tickets in March?"

→ group_and_rank
→ group_by = agent_id
→ status = Resolved
→ month = 3


"Rank agents by resolved tickets in March."

→ group_and_rank
→ group_by = agent_id
→ status = Resolved
→ month = 3


resolution_rate
---------------

Use for resolution rate questions.

Example:

"What is the resolution rate by category?"

→ resolution_rate
→ group_by = category


detect_resolution_anomalies
---------------------------

Use for abnormal or unusual resolution-time
questions.

Examples:

"Find abnormal resolution times."

"Are there any anomalies in resolution times?"

"Are there any anomalies in resolution times
this week?"

For "this week":

→ operation = detect_resolution_anomalies
→ time_period = this_week

The Python application calculates the actual
date range from the dataset.


unresolved_high_priority_tickets
--------------------------------

Use for unresolved High or Critical tickets
older than a specified number of hours.

High-priority means:

High OR Critical.

Example:

"Find unresolved high-priority tickets older
than 24 hours."

→ unresolved_high_priority_tickets
→ max_resolution_time_hrs = "24"


"Find unresolved Critical tickets older than
24 hours."

→ unresolved_high_priority_tickets
→ priority = Critical
→ max_resolution_time_hrs = "24"


DATASET
-------

The dataset contains data from 2024.

Columns:

ticket_id
created_at
category
priority
status
response_time_hrs
resolution_time_hrs
agent_id
customer_rating
issue_summary


ALLOWED STATUS
--------------

Open
Resolved
Escalated


ALLOWED PRIORITY
----------------

Low
Medium
High
Critical


ALLOWED CATEGORY
----------------

Billing
Technical
General


ALLOWED GROUP BY
----------------

agent_id
category
priority
status


MONTH
-----

Use numbers 1-12.

January = 1
February = 2
March = 3
April = 4
May = 5
June = 6
July = 7
August = 8
September = 9
October = 10
November = 11
December = 12


TIME PERIOD
-----------

Allowed values:

""
"this_week"

Use "this_week" only when the user explicitly
asks for "this week".

The Python application calculates the date
range from the dataset.

Do not calculate dates yourself.


FINAL OPERATION RULE
--------------------

If max_resolution_time_hrs is greater than "0",
the operation MUST be either:

get_tickets

OR

unresolved_high_priority_tickets

NEVER use count_tickets when a resolution-time
condition exists.

If the question contains "unresolved" together
with a count request, use get_tickets.

If the question contains "took more than X hours"
or "not resolved within X hours", use get_tickets.


OUTPUT RULES
------------

Return ONLY valid JSON.

Do not include explanations.

Do not answer the question.

For unused string fields use "".

For unused month use 0.

For unused time_period use "".

max_resolution_time_hrs MUST always be a STRING.

For unused threshold use "0".
"""

        response_schema = {
            "type": "object",
            "properties": {

                "operation": {
                    "type": "string",
                    "enum": [
                        "count_tickets",
                        "get_tickets",
                        "average_rating",
                        "average_rating_by_group",
                        "group_and_rank",
                        "resolution_rate",
                        "detect_resolution_anomalies",
                        "unresolved_high_priority_tickets",
                        "unsupported"
                    ]
                },

                "status": {
                    "type": "string"
                },

                "priority": {
                    "type": "string"
                },

                "category": {
                    "type": "string"
                },

                "group_by": {
                    "type": "string"
                },

                "month": {
                    "type": "integer"
                },

                "max_resolution_time_hrs": {
                    "type": "string"
                },

                "time_period": {
                    "type": "string",
                    "enum": [
                        "",
                        "this_week"
                    ]
                }
            },

            "required": [
                "operation",
                "status",
                "priority",
                "category",
                "group_by",
                "month",
                "max_resolution_time_hrs",
                "time_period"
            ],

            "additionalProperties": False
        }

        response = self.client.chat.completions.create(
            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ],

            response_format={
                "type": "json_schema",

                "json_schema": {
                    "name": "ticket_query",
                    "strict": True,
                    "schema": response_schema
                }
            },

            temperature=0
        )

        content = response.choices[0].message.content

        result = json.loads(content)

        return result