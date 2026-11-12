"""FastAPI service for AapdaMitra — Day 04."""
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from Day02.app.smart_search import rank_records

ROOT = Path(__file__).resolve().parent.parent
RECORDS_FILE = ROOT / "data" / "records.jsonl"

app = FastAPI(
    title="AapdaMitra API",
    description="Disaster-preparedness action records and question search.",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


def load_records() -> list[dict[str, Any]]:
    """Load validated JSONL records; use Day 02 sample records if JSONL is absent."""
    records = []

    if RECORDS_FILE.exists():
        with RECORDS_FILE.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    if isinstance(item, dict) and "id" in item and "action" in item:
                        records.append(item)
                except json.JSONDecodeError:
                    print(f"[WARN] Skipping invalid JSON on line {line_number}")
        return records

    # Keeps the API usable before Day 03 ingestion has generated records.jsonl.
    from Day02.app.records import load_records as load_day02_records
    return load_day02_records()


@app.get("/health")
def health():
    return {"status": "ok", "service": "AapdaMitra API"}


@app.get("/records")
def get_records(limit: int = Query(default=20, ge=1, le=500)):
    records = load_records()
    return {"count": min(limit, len(records)), "records": records[:limit]}


@app.get("/records/{record_id}")
def get_record(record_id: int):
    for record in load_records():
        if record.get("id") == record_id:
            return record
    raise HTTPException(status_code=404, detail="Record not found")


@app.get("/search")
def search(q: str = Query(min_length=1, max_length=200)):
    results = rank_records(q, load_records())
    return {"query": q, "count": len(results), "results": results}


@app.post("/questions")
def ask_question(payload: QuestionRequest):
    results = rank_records(payload.question, load_records())
    return {
        "question": payload.question,
        "count": len(results),
        "message": (
            "Here are the most relevant candidate safety records. "
            "Check the original NDMA source and local authority instructions."
            if results else
            "No matching records found. Try another disaster or safety keyword."
        ),
        "results": results,
    }
