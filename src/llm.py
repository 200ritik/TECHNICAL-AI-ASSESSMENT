import os
import json

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class TicketLLM:

    def __init__(self):

        # ------------------------------------------
        # Get API key
        # ------------------------------------------

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in .env file."
            )

        # ------------------------------------------
        # Initialize Groq client
        # ------------------------------------------

        self.client = Groq(
            api_key=api_key
        )

        # ------------------------------------------
        # Model
        # ------------------------------------------

        self.model = "openai/gpt-oss-20b"

    # --------------------------------------------------
    # Understand natural language query
    # --------------------------------------------------

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

--------------------------------------------------
AVAILABLE OPERATIONS
--------------------------------------------------

1. count_tickets

Use this when the user asks how many tickets
match one or more basic filters.

Examples:

"How many tickets are open?"

"How many critical tickets are there?"

"How many Technical tickets are open?"

--------------------------------------------------

2. get_tickets

Use this when the user asks to find, list, show,
or count tickets based on priority and/or
resolution time.

IMPORTANT:

Use get_tickets when the question contains:

- unresolved tickets
- resolution time
- tickets taking more than X hours
- tickets taking longer than X hours
- tickets that were not resolved within X hours
- priority + resolution-time conditions

An unresolved ticket means:

resolution_time_hrs is null.

When max_resolution_time_hrs is provided, the
Python query engine will return:

- unresolved tickets
OR
- tickets whose resolution_time_hrs is greater
  than the specified threshold.

Examples:

User:
"How many critical tickets are unresolved?"

Output:
{
  "operation": "get_tickets",
  "status": "",
  "priority": "Critical",
  "category": "",
  "group_by": "",
  "month": 0,
  "max_resolution_time_hrs": "0"
}

User:
"How many critical tickets took more than 12 hours to resolve?"

Output:
{
  "operation": "get_tickets",
  "status": "",
  "priority": "Critical",
  "category": "",
  "group_by": "",
  "month": 0,
  "max_resolution_time_hrs": "12"
}

User:
"How many critical tickets are unresolved or took more than 12 hours to resolve?"

Output:
{
  "operation": "get_tickets",
  "status": "",
  "priority": "Critical",
  "category": "",
  "group_by": "",
  "month": 0,
  "max_resolution_time_hrs": "12"
}

User:
"Show critical tickets that took more than 24 hours."

Output:
{
  "operation": "get_tickets",
  "status": "",
  "priority": "Critical",
  "category": "",
  "group_by": "",
  "month": 0,
  "max_resolution_time_hrs": "24"
}

--------------------------------------------------
3. average_rating
--------------------------------------------------

Use this when the user asks for the average
customer rating.

Examples:

"What is the average customer rating?"

"What is the average rating for Technical tickets?"

"What is the average rating for Billing tickets?"

--------------------------------------------------
4. group_and_rank
--------------------------------------------------

Use this when the user asks to group, rank,
compare, or order tickets by an attribute.

Possible group_by values:

- agent_id
- category
- priority
- status

Examples:

"Rank agents by resolved tickets."

"Which agents handled the most tickets?"

"Rank agents by resolved tickets in March."

If the question says March, use:

"month": 3

If the question says January, use:

"month": 1

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

The dataset is from 2024, so month filtering
must use the year 2024.

--------------------------------------------------
5. resolution_rate
--------------------------------------------------

Use this when the user asks for resolution rate.

Examples:

"What is the resolution rate by category?"

"Show resolution rate for each category."

"Which category has the highest resolution rate?"

If grouping by category:

"group_by": "category"

--------------------------------------------------
6. detect_resolution_anomalies
--------------------------------------------------

Use this when the user asks to find abnormal,
unusual, or anomalous resolution times.

Examples:

"Find abnormal resolution times."

"Detect resolution time anomalies."

"Which tickets have unusual resolution times?"

--------------------------------------------------
7. unsupported
--------------------------------------------------

Use this when the question cannot be answered
using the available operations and dataset.

--------------------------------------------------
AVAILABLE DATASET COLUMNS
--------------------------------------------------

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

--------------------------------------------------
ALLOWED VALUES
--------------------------------------------------

Status:

Open
Resolved
Escalated

Priority:

Low
Medium
High
Critical

Category:

Billing
Technical
General

Group by:

agent_id
category
priority
status

--------------------------------------------------
OUTPUT RULES
--------------------------------------------------

You MUST return JSON matching the provided schema.

For unused string fields use:

""

For an unused month use:

0

For an unused resolution threshold use:

"0"

max_resolution_time_hrs MUST always be a STRING.

For example:

"12"

NOT:

12

--------------------------------------------------
IMPORTANT
--------------------------------------------------

Do not answer the question.

Only return the structured JSON.

Do not include explanations.

Do not include markdown.

--------------------------------------------------
FINAL EXAMPLE
--------------------------------------------------

User:
"How many tickets are currently open?"

Return:

{
  "operation": "count_tickets",
  "status": "Open",
  "priority": "",
  "category": "",
  "group_by": "",
  "month": 0,
  "max_resolution_time_hrs": "0"
}
"""

        # ------------------------------------------
        # JSON schema
        # ------------------------------------------

        response_schema = {

            "type": "object",

            "properties": {

                "operation": {
                    "type": "string",
                    "enum": [
                        "count_tickets",
                        "get_tickets",
                        "average_rating",
                        "group_and_rank",
                        "resolution_rate",
                        "detect_resolution_anomalies",
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
                }
            },

            "required": [
                "operation",
                "status",
                "priority",
                "category",
                "group_by",
                "month",
                "max_resolution_time_hrs"
            ],

            "additionalProperties": False
        }

        # ------------------------------------------
        # Call Groq
        # ------------------------------------------

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

        # ------------------------------------------
        # Extract response
        # ------------------------------------------

        content = response.choices[0].message.content

        # ------------------------------------------
        # Convert JSON string to Python dictionary
        # ------------------------------------------

        result = json.loads(content)

        return result