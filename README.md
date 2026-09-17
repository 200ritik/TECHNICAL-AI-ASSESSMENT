# TECHNICAL-AI-ASSESSMENT
# AI Customer Support Ticket System

An AI-powered customer support ticket analysis system that allows users to ask natural-language questions about support tickets and automatically detect resolution-time anomalies.

The system uses an LLM to understand the user's question and converts it into a structured query. The actual data analysis is performed using Python and Pandas rather than relying on the LLM to calculate results.

## Features

- Natural-language querying of support ticket data
- LLM-based query understanding
- Ticket filtering by:
  - Status
  - Priority
  - Category
  - Resolution time
- Ticket counting
- Average customer rating analysis
- Agent-based ticket ranking
- Resolution-rate analysis
- Resolution-time anomaly detection
- REST API using FastAPI
- Minimal chat interface using Streamlit
- Structured JSON responses
- Query validation before execution
- Handles unresolved tickets with missing resolution times

## Architecture

```text
                     User
                       |
                       v
                Streamlit UI
                       |
                       v
                FastAPI REST API
                       |
                       v
                 Dispatcher
                 /         \
                /           \
               v             v
          Groq LLM      Query Engine
               |             |
               |             v
               |          Pandas
               |             |
               \             /
                \           /
                 v         v
                    Result
                       |
                       v
                  FastAPI
                       |
                       v
                 Streamlit UI