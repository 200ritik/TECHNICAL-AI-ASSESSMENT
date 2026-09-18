from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.dispatcher import TicketDispatcher


app = FastAPI(
    title="AI Customer Support Ticket API",
    description=(
        "Natural language API for querying "
        "customer support ticket data and "
        "detecting anomalies."
    ),
    version="1.0.0"
)


dispatcher = TicketDispatcher()


class QuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description=(
            "Natural language question about "
            "the ticket dataset."
        )
    )


class QuestionResponse(BaseModel):

    question: str
    query: dict
    result: object


@app.get("/")
def root():

    return {
        "message":
            "AI Customer Support Ticket API",

        "status":
            "running",

        "docs":
            "/docs"
    }


@app.get("/health")
def health_check():

    return {
        "status":
            "healthy"
    }


@app.post(
    "/ask",
    response_model=QuestionResponse
)
def ask_question(
    request: QuestionRequest
):

    try:

        result = dispatcher.ask(
            request.question
        )

        return {
            "question":
                request.question,

            "query":
                result["query"],

            "result":
                result["result"]
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error."
        )


@app.get("/anomalies")
def get_anomalies():

    try:

        result = (
            dispatcher
            .engine
            .detect_resolution_anomalies()
        )

        return {
            "count": len(result),
            "anomalies":
                dispatcher.format_result(result)
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to detect anomalies."
        )