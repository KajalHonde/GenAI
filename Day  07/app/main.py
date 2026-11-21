
"""AapdaMitra API."""

import time
import uuid

from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.graph import graph as agent_graph
from app.graph import run_agent
from app.observability import (
    INJECTION_REFUSAL,
    MAX_QUESTION_LENGTH,
    is_prompt_injection,
    metrics_summary,
    record_request,
)
from app.rag import router as rag_router
from app.search_api import router as search_router

app = FastAPI(
    title="AapdaMitra API",
    description="Disaster safety search, RAG and LangGraph agent.",
    version="2.1.0"
)


# Existing APIs
app.include_router(search_router)
app.include_router(rag_router)


# Agent request model
class AgentRequest(BaseModel):
    question: str | None = Field(
        default=None, max_length=MAX_QUESTION_LENGTH
    )
    temperature: float | None = None
    humidity: float | None = None
    thread_id: str | None = None
    approval: bool | None = None


# POST /agent
@app.post("/agent")
def agent_endpoint(request: AgentRequest):

    # ----------------------------------
    # FIRST REQUEST: Start the agent
    # ----------------------------------
    if request.approval is None:

        if not request.question:
            raise HTTPException(
                status_code=400,
                detail="Please provide a question."
            )

        # Prompt-injection guard: refuse before the agent runs.
        if is_prompt_injection(request.question):
            record_request(
                "/agent", 0.0, blocked=True, status="blocked"
            )
            return {
                "status": "blocked",
                "thread_id": request.thread_id,
                "message": INJECTION_REFUSAL
            }

        thread_id = request.thread_id or str(uuid.uuid4())
        start = time.perf_counter()

        try:
            response = run_agent(
                question=request.question,
                temperature=request.temperature,
                humidity=request.humidity,
                thread_id=thread_id
            )
        except Exception as e:  # noqa: BLE001
            latency = (time.perf_counter() - start) * 1000
            record_request("/agent", latency, status="error")
            raise HTTPException(
                status_code=500,
                detail=f"Agent execution failed: {e!s}"
            )

        latency = (time.perf_counter() - start) * 1000
        record_request("/agent", latency, status="ok")

    # ----------------------------------
    # SECOND REQUEST: Approval / Rejection
    # ----------------------------------
    else:

        if not request.thread_id:
            raise HTTPException(
                status_code=400,
                detail="thread_id is required for approval."
            )

        thread_id = request.thread_id

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        try:
            # Resume the interrupted graph.
            response = agent_graph.invoke(
                Command(resume=request.approval),
                config=config
            )
        except Exception as e:  # noqa: BLE001
            raise HTTPException(
                status_code=500,
                detail=f"Approval processing failed: {e!s}"
            )

        # Explicit rejection response
        if request.approval is False:
            return {
                "status": "rejected",
                "thread_id": thread_id,
                "message": "Tool execution was not approved."
            }

    # ----------------------------------
    # CHECK FOR HUMAN APPROVAL
    # ----------------------------------
    if "__interrupt__" in response:

        approval_details = []

        for item in response["__interrupt__"]:
            approval_details.append(item.value)

        return {
            "status": "approval_required",
            "thread_id": thread_id,
            "approval_request": approval_details
        }

    # ----------------------------------
    # COMPLETED RESPONSE
    # ----------------------------------
    return {
        "status": "completed",
        "thread_id": thread_id,
        "decision": response.get("decision"),
        "result": response.get("result")
    }


# HOME
@app.get("/")
def home():
    return {
        "message": "Welcome to AapdaMitra API",
        "health": "/health",
        "semantic_search": "/search/semantic?q=earthquake safety",
        "ask": "/ask",
        "agent": "/agent",
        "metrics": "/metrics",
        "documentation": "/docs"
    }


# HEALTH CHECK
@app.get("/health")
def health():
    return {"status": "ok"}


# METRICS
@app.get("/metrics")
def metrics():
    """Return aggregated request metrics (latency, tokens, cache, blocks)."""
    return metrics_summary()
