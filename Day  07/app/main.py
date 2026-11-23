"""AapdaMitra API."""

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from langgraph.types import Command
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

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
from app.vectorstore import collection

logger = logging.getLogger("aapdamitra.startup")

# ---------------------------------------------------------------------------
# Public endpoints that do NOT require the API key.
# Render needs /health to pass its health check without credentials.
# ---------------------------------------------------------------------------
_PUBLIC_PATHS = {"/health", "/"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Reject every request that lacks the correct X-API-Key header.

    The key is set via the API_SECRET_KEY environment variable on Render.
    If that variable is not set (e.g. local dev without a .env), the
    middleware is disabled so local development still works without config.
    """

    async def dispatch(self, request: Request, call_next):
        secret = os.getenv("API_SECRET_KEY", "")

        # Middleware is disabled when the env var is not configured.
        if not secret:
            return await call_next(request)

        # Public paths are always allowed.
        if request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        # Check the header.
        provided = request.headers.get("X-API-Key", "")
        if provided != secret:
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden: invalid or missing API key."},
            )

        return await call_next(request)


def _auto_index() -> None:
    """Index NDMA documents if the vector store is empty."""
    try:
        if collection.count() > 0:
            logger.info(
                "Vector store already has %d chunks — skipping index.",
                collection.count(),
            )
            return

        logger.info("Vector store is empty — building index from documents/...")
        from app.chunking import create_chunks, load_documents
        from app.vectorstore import add_documents

        docs_path = Path(__file__).resolve().parents[1] / "documents"
        documents = load_documents(docs_path)
        chunks = create_chunks(documents, chunk_size=100)

        if chunks:
            add_documents(chunks)
            logger.info("Indexed %d chunks.", len(chunks))
        else:
            logger.warning(
                "No documents found in %s — vector store remains empty.", docs_path
            )

    except Exception as exc:  # noqa: BLE001
        logger.error("Auto-index failed: %s", exc)


@asynccontextmanager
async def lifespan(application: FastAPI):
    _auto_index()
    yield


app = FastAPI(
    title="AapdaMitra API",
    description="Disaster safety search, RAG and LangGraph agent.",
    version="2.2.0",
    lifespan=lifespan,
)

# Register the API key guard before all routes.
app.add_middleware(APIKeyMiddleware)

app.include_router(search_router)
app.include_router(rag_router)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
class AgentRequest(BaseModel):
    question: str | None = Field(default=None, max_length=MAX_QUESTION_LENGTH)
    temperature: float | None = None
    humidity: float | None = None
    thread_id: str | None = None
    approval: bool | None = None


@app.post("/agent")
def agent_endpoint(request: AgentRequest):

    if request.approval is None:

        if not request.question:
            raise HTTPException(status_code=400, detail="Please provide a question.")

        if is_prompt_injection(request.question):
            record_request("/agent", 0.0, blocked=True, status="blocked")
            return {
                "status": "blocked",
                "thread_id": request.thread_id,
                "message": INJECTION_REFUSAL,
            }

        thread_id = request.thread_id or str(uuid.uuid4())
        start = time.perf_counter()

        try:
            response = run_agent(
                question=request.question,
                temperature=request.temperature,
                humidity=request.humidity,
                thread_id=thread_id,
            )
        except Exception as e:  # noqa: BLE001
            latency = (time.perf_counter() - start) * 1000
            record_request("/agent", latency, status="error")
            raise HTTPException(
                status_code=500, detail=f"Agent execution failed: {e!s}"
            )

        latency = (time.perf_counter() - start) * 1000
        record_request("/agent", latency, status="ok")

    else:

        if not request.thread_id:
            raise HTTPException(
                status_code=400, detail="thread_id is required for approval."
            )

        thread_id = request.thread_id
        config = {"configurable": {"thread_id": thread_id}}

        try:
            response = agent_graph.invoke(Command(resume=request.approval), config=config)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(
                status_code=500, detail=f"Approval processing failed: {e!s}"
            )

        if request.approval is False:
            return {
                "status": "rejected",
                "thread_id": thread_id,
                "message": "Tool execution was not approved.",
            }

    if "__interrupt__" in response:
        return {
            "status": "approval_required",
            "thread_id": thread_id,
            "approval_request": [item.value for item in response["__interrupt__"]],
        }

    return {
        "status": "completed",
        "thread_id": thread_id,
        "decision": response.get("decision"),
        "result": response.get("result"),
    }


# ---------------------------------------------------------------------------
# Utility endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "Welcome to AapdaMitra API",
        "health": "/health",
        "semantic_search": "/search/semantic?q=earthquake safety",
        "ask": "/ask",
        "agent": "/agent",
        "metrics": "/metrics",
        "documentation": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    """Return aggregated request metrics (latency, tokens, cache, blocks)."""
    return metrics_summary()


# ---------------------------------------------------------------------------
# Feedback store — kept in memory for the lifetime of the container.
# Protected by the API key so only you can read responses.
# ---------------------------------------------------------------------------
_feedback: list[dict] = []
_feedback_lock = __import__("threading").Lock()


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: str  # "up" or "down"
    timestamp: str = ""


@app.post("/feedback")
def post_feedback(body: FeedbackRequest):
    """Save one thumbs-up / thumbs-down record."""
    import datetime

    record = {
        "timestamp": body.timestamp or datetime.datetime.now().isoformat(
            timespec="seconds"
        ),
        "question": body.question,
        "answer": body.answer,
        "rating": body.rating,
    }
    with _feedback_lock:
        _feedback.append(record)
    return {"status": "saved", "total": len(_feedback)}


@app.get("/feedback")
def get_feedback(rating: str | None = None):
    """Return all feedback records. Optionally filter by rating=up or rating=down."""
    with _feedback_lock:
        records = list(_feedback)
    if rating:
        records = [r for r in records if r["rating"] == rating]
    return {
        "total": len(records),
        "thumbs_up": sum(1 for r in _feedback if r["rating"] == "up"),
        "thumbs_down": sum(1 for r in _feedback if r["rating"] == "down"),
        "records": records,
    }

