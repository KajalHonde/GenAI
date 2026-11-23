"""AapdaMitra FastAPI service — Day 04.

Endpoints
---------
GET  /health                  liveness check
GET  /records?limit=           list records (default 20, max 100)
GET  /records/{id}             single record, 404 if missing
GET  /search?q=                TF-IDF keyword search over records
POST /questions                accept a user question and echo back
GET  /questions                list the 10 AapdaMitra sample questions
"""

import sys
from pathlib import Path

# Allow importing from the Day02 package tree.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from Day02.app.records import get_by_id, load_records
from Day02.app.smart_search import rank_records

app = FastAPI(
    title="AapdaMitra API",
    description="Disaster safety records, search and Q&A.",
    version="1.0.0",
)

SAMPLE_QUESTIONS = [
    "What should I do during a flood?",
    "What precautions should I take during heavy rainfall?",
    "How can I stay safe during an earthquake?",
    "What should I keep in an emergency kit?",
    "What should I do if my house gets flooded?",
    "Is the bridge near my village currently open or closed?",
    "What should I do if I see a landslide?",
    "How can I help an injured person during a disaster?",
    "Where should I go during an emergency evacuation?",
    "What emergency items should I carry while evacuating?",
]


class QuestionRequest(BaseModel):
    question: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
def home():
    return {
        "message": "Welcome to AapdaMitra",
        "endpoints": ["/health", "/records", "/search", "/questions"],
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "AapdaMitra is running"}


@app.get("/records")
def list_records(
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return")
):
    """Return up to *limit* action records."""
    return load_records()[:limit]


@app.get("/records/{record_id}")
def get_record(record_id: int):
    """Return one record by numeric ID, or 404 if it does not exist."""
    record = get_by_id(record_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Record {record_id} not found.",
        )
    return record


@app.get("/search")
def search_records(
    q: str = Query(..., min_length=1, description="Keyword or phrase to search")
):
    """Return records ranked by TF-IDF cosine similarity to the query."""
    all_records = load_records()
    results = rank_records(q, all_records)
    return {
        "query": q,
        "total_results": len(results),
        "results": results,
    }


@app.get("/questions")
def get_questions():
    """Return the 10 real AapdaMitra user questions (Q6 is unanswerable)."""
    return {
        "total": len(SAMPLE_QUESTIONS),
        "note": "Q6 is a question the data cannot answer (live bridge status).",
        "questions": [
            {"id": f"Q{i + 1}", "question": q}
            for i, q in enumerate(SAMPLE_QUESTIONS)
        ],
    }


@app.post("/questions")
def post_question(body: QuestionRequest):
    """Accept a user question and return a holding acknowledgement.

    In later days this endpoint is replaced by /ask (RAG with citations).
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    return {
        "received": body.question,
        "status": "queued",
        "note": (
            "Full RAG answers are available at POST /ask in the Day 07 service."
        ),
    }
