AI Customer Support Ticket Assistant

An AI-powered customer support ticket analysis system that allows users
to ask natural-language questions about a CSV dataset, detect
resolution-time anomalies, and access the functionality through both a
REST API and a Streamlit UI.

Features

CSV dataset ingestion using Pandas

Natural-language query understanding using an LLM

Structured query generation from user questions

Safe query validation before execution

Pandas-based deterministic query execution

Customer-rating analysis

Ticket counting and filtering

Agent ranking

Resolution-rate analysis

Resolution-time anomaly detection using the IQR method

Detection of unresolved high-priority tickets older than a specified
number of hours

REST API using FastAPI

Interactive UI using Streamlit

Health-check endpoint

No RAG or vector database required for the structured CSV analysis

Architecture

                    User Question
                         |
                         v
                +------------------+
                |    Streamlit UI  |
                +--------+---------+
                         |
                         v
                +------------------+
                |    FastAPI API   |
                +--------+---------+
                         |
                         v
                +------------------+
                |    Dispatcher    |
                +--------+---------+
                         |
             +-----------+-----------+
             |                       |
             v                       v
      +-------------+         +-------------+
      |    Ticket   |         |    Query    |
      |     LLM     |         | Validation  |
      +------+------+         +------+------+
             |                       |
             +-----------+-----------+
                         |
                         v
                +------------------+
                |  Pandas Query    |
                |     Engine      |
                +--------+---------+
                         |
                         v
                +------------------+
                | support_tickets  |
                |      .csv        |
                +------------------+

Query flow

The user submits a natural-language question.

The LLM converts the question into a structured JSON query.

The dispatcher validates the generated query against allowed
operations, fields, and values.

Pandas executes the validated query against the actual CSV data.

The result is formatted into JSON-compatible data.

FastAPI returns the result to the UI or API client.

The LLM does not calculate ticket counts, averages, rankings, or
anomaly values. It only interprets the user's natural-language question.

Project Structure

TECHNICAL-AI-ASSESSMENT/
│
├── data/
│   └── support_tickets.csv
│
├── src/
│   ├── __init__.py
│   ├── ingestion.py
│   ├── query_engine.py
│   ├── llm.py
│   └── dispatcher.py
│
├── api/
│   ├── __init__.py
│   └── main.py
│
├── ui/
│   └── app.py
│
├── test_cases/
│   ├── test1.py
│   └── test_dispatcher.py
│
├── .env
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── run.py

Dataset

The system uses support_tickets.csv.

The dataset contains 500 customer support tickets with the following
columns:

Column                              Description

ticket_id                         Unique ticket identifier

created_at                        Ticket creation date and time

category                          Billing, Technical, or General

priority                          Low, Medium, High, or Critical

status                            Open, Resolved, or Escalated

response_time_hrs                 Time taken to respond

resolution_time_hrs               Time taken to resolve; null for
unresolved tickets

agent_id                          Support agent identifier

customer_rating                   Customer rating when available

Technology Stack

Programming Language

Python

Data Processing

Pandas

NumPy

LLM

Groq API

Model: openai/gpt-oss-20b

The LLM is used for natural-language understanding and structured query
generation.

Backend

FastAPI

Uvicorn

Frontend

Streamlit

Configuration

python-dotenv

HTTP Client

Requests

Why the LLM Does Not Query the CSV Directly

The system separates language understanding from data execution.

Instead of sending the complete CSV to the LLM, the LLM produces a
structured query such as:

{
  "operation": "count_tickets",
  "status": "Open",
  "priority": "",
  "category": "",
  "group_by": "",
  "month": 0,
  "max_resolution_time_hrs": "0",
  "time_period": ""
}

The Python application validates this structure and executes the actual
operation using Pandas.

This approach keeps numerical operations deterministic and prevents the
LLM from inventing results.

Supported Operations

The system currently supports:

count_tickets

get_tickets

average_rating

average_rating_by_group

group_and_rank

resolution_rate

detect_resolution_anomalies

unresolved_high_priority_tickets

Unsupported questions are returned as unsupported instead of being
answered using information outside the dataset.

Example Queries

Count open tickets

Question

How many tickets are currently open?

Example result

111 tickets

Average rating

Question

What is the average customer rating for Technical category tickets?

Example result

3.74

Agent ranking

Question

Which agent resolved the most tickets in March?

The system groups resolved tickets by agent_id, filters March records,
and ranks the agents by ticket count.

Resolution-time filtering

Question

Show me all Critical tickets not resolved within 12 hours.

The LLM generates a structured resolution-time query, and the Python
query engine performs the filtering.

Resolution anomalies

Question

Are there any anomalies in resolution times this week?

The system identifies the requested time period and the query engine
calculates anomalies using the IQR method.

High-priority unresolved tickets

Question

Find unresolved high-priority tickets older than 24 hours.

The system checks unresolved High and Critical priority tickets and
compares their age against the specified threshold.

Anomaly Detection

Resolution-time anomalies are detected using the Interquartile Range
(IQR) method.

IQR = Q3 - Q1

Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR

Records with resolution times outside these bounds are flagged as
anomalies.

Unresolved tickets are excluded from resolution-time anomaly
calculations because they do not have a resolution_time_hrs value.

REST API

Start the FastAPI server:

python -m uvicorn api.main:app --reload

API documentation:

http://127.0.0.1:8000/docs

1. Health Check

GET /health

Example response:

{
  "status": "healthy"
}

2. Natural-Language Query

POST /ask

Request:

{
  "question": "How many tickets are currently open?"
}

Example response:

{
  "question": "How many tickets are currently open?",
  "query": {
    "operation": "count_tickets",
    "status": "Open",
    "priority": "",
    "category": "",
    "group_by": "",
    "month": 0,
    "max_resolution_time_hrs": 0.0,
    "time_period": ""
  },
  "result": 111
}

3. Anomaly Detection

GET /anomalies

Example response structure:

{
  "count": 21,
  "anomalies": []
}

The anomalies field contains the actual flagged ticket records.

Streamlit UI

Start the UI:

python -m streamlit run ui/app.py

The application will normally be available at:

http://localhost:8501

The UI provides:

Chat-style natural-language interaction

Conversation history

Ticket count results

Average values

Grouped results

Ticket tables for list/filter queries

API error handling

Running the Complete Application

The project includes run.py for starting both the FastAPI backend and
Streamlit UI.

Run:

python run.py

This starts:

FastAPI on http://127.0.0.1:8000

Streamlit on http://localhost:8501

Environment Setup

Create a Python virtual environment:

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key

Do not commit the .env file to GitHub.

Testing

The dispatcher has tests covering the main query operations.

Run:

python -m test_cases.test_dispatcher

The current test suite covers:

Open ticket count

Critical tickets with resolution-time conditions

Average Technical customer rating

Agent ranking for resolved March tickets

Resolution rate by category

Resolution-time anomaly detection

Average rating by agent

Unresolved high-priority tickets older than 24 hours

Expected test completion message:

==============================
ALL DISPATCHER TESTS PASSED
==============================

Security and Reliability Considerations

The LLM is not allowed to directly execute Python or Pandas
operations.

The LLM only generates structured JSON.

Generated queries are validated before execution.

Allowed operations are explicitly defined.

Allowed status, priority, category, and grouping values are
validated.

The application executes queries locally against the known CSV
dataset.

The complete dataset is not sent to the LLM for every question.

API errors are handled using appropriate HTTP responses.

Known Limitations

The system currently works with the provided CSV dataset.

The LLM requires a valid Groq API key.

Internet access is required for LLM requests.

The current application does not use a persistent database.

The dataset is relatively small and is loaded into memory using
Pandas.

Natural-language questions outside the supported dataset operations
may be classified as unsupported.

The dataset contains records from 2024, so time-based questions are
interpreted using the dataset's available dates.

The "current age" calculation for unresolved tickets uses the latest
timestamp available in the dataset rather than real-world current
time.

Resolution-time anomaly detection uses statistical IQR thresholds
and does not represent a business-defined SLA.

Design Decisions

Why Pandas?

The dataset is a structured CSV with only 500 records. Pandas provides
reliable filtering, grouping, aggregation, and statistical calculations
without introducing unnecessary infrastructure.

Why use an LLM?

Natural-language understanding is a core requirement of the assessment.
The LLM allows users to ask questions naturally instead of writing
filters or Python expressions.

Why not use RAG?

The primary questions are structured analytical queries involving
counts, averages, filtering, grouping, ranking, and anomaly detection.

For these operations, executing deterministic Pandas queries against the
structured dataset is more appropriate than retrieving text chunks
through a vector database.

Future Improvements

Possible production extensions include:

Database-backed ticket storage

Authentication and user management

Background data ingestion

More advanced anomaly detection

Configurable business/SLA thresholds

Additional natural-language query types

Automated API and integration tests

Containerized deployment

Monitoring and logging

Support for larger datasets

Conclusion

This project demonstrates an AI-powered natural-language interface for
customer support analytics while keeping the actual data processing
deterministic and controlled.

The system combines:

LLM
+
Structured Query Validation
+
Pandas
+
FastAPI
+
Streamlit

to provide a simple end-to-end AI customer support ticket analysis
application.