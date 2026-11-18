
"""AapdaMitra API."""

import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from langgraph.types import Command

from app.search_api import router as search_router
from app.rag import router as rag_router
from app.graph import graph as agent_graph
from app.graph import run_agent


app = FastAPI(
    title="AapdaMitra API",
    description="Disaster safety search, RAG and LangGraph agent.",
    version="2.0.0"
)


# Existing APIs
app.include_router(search_router)
app.include_router(rag_router)


# Agent request model
class AgentRequest(BaseModel):

    question: Optional[str] = None

    temperature: Optional[float] = None

    humidity: Optional[float] = None

    thread_id: Optional[str] = None

    approval: Optional[bool] = None


# POST /agent
@app.post("/agent")
def agent_endpoint(request: AgentRequest):

    # First request: Start the agent
    if request.approval is None:

        if not request.question:
            raise HTTPException(
                status_code=400,
                detail="Please provide a question."
            )

        thread_id = request.thread_id or str(uuid.uuid4())

        response = run_agent(
            question=request.question,
            temperature=request.temperature,
            humidity=request.humidity,
            thread_id=thread_id
        )

    # Second request: Resume after human approval
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

        response = agent_graph.invoke(
            Command(resume=request.approval),
            config=config
        )

        if request.approval is False:
            return {
                "status": "rejected",
                "thread_id": thread_id,
                "message": "Tool execution was not approved."
            }

    # Check whether human approval is required
    if "__interrupt__" in response:

        approval_details = []

        for item in response["__interrupt__"]:
            approval_details.append(item.value)

        return {
            "status": "approval_required",
            "thread_id": thread_id,
            "approval_request": approval_details
        }

    # Return completed result
    return {
        "status": "completed",
        "thread_id": thread_id,
        "decision": response.get("decision"),
        "result": response.get("result")
    }


@app.get("/")
def home():

    return {
        "message": "Welcome to AapdaMitra API",
        "health": "/health",
        "semantic_search": "/search/semantic?q=earthquake safety",
        "ask": "/ask",
        "agent": "/agent",
        "documentation": "/docs"
    }


@app.get("/health")
def health():

    return {"status": "ok"}
