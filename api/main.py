from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.dispatcher import TicketDispatcher


# --------------------------------------------------
# Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="AI Customer Support Ticket API",
    description=(
        "Natural language API for querying "
        "customer support ticket data and "
        "detecting resolution-time anomalies."
    ),
    version="1.0.0"
)


# --------------------------------------------------
# Initialize dispatcher
# --------------------------------------------------

dispatcher = TicketDispatcher()


# --------------------------------------------------
# Request schema
# --------------------------------------------------

class QuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="Natural language question about the ticket dataset."
    )


# --------------------------------------------------
# Response schema
# --------------------------------------------------

class QuestionResponse(BaseModel):

    question: str

    query: dict

    result: object


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "AI Customer Support Ticket API",
        "status": "running",
        "docs": "/docs"
    }


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# Ask question
# --------------------------------------------------

@app.post(
    "/ask",
    response_model=QuestionResponse
)
def ask_question(request: QuestionRequest):

    try:

        result = dispatcher.ask(
            request.question
        )

        return {
            "question": request.question,
            "query": result["query"],
            "result": result["result"]
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail="Internal server error."
        )