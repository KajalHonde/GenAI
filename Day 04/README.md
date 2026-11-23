# AapdaMitra — Day 04: FastAPI Service

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/records?limit=` | List action records (default 20, max 100) |
| `GET` | `/records/{id}` | Single record — 404 if missing |
| `GET` | `/search?q=` | TF-IDF cosine search over records |
| `GET` | `/questions` | List the 10 AapdaMitra sample questions |
| `POST` | `/questions` | Submit a question (echoed back with status) |

## How to run

Install dependencies (from the repo root):

```bash
pip install -r "Day 04/requirements.txt"
```

Start the API:

```bash
uvicorn "Day 04.main:app" --reload
```

Or from inside the `Day 04` directory:

```bash
cd "Day 04"
uvicorn main:app --reload
```

Open the interactive docs at <http://localhost:8000/docs>.

## Smart search

`/search?q=` is backed by `Day02/app/smart_search.py` which uses
TF-IDF vectorisation and cosine similarity from scikit-learn to rank
records against the query. It is the same module that powers the
semantic search in later days.

## Notes

This service reads records from `Day02/data/records.json` (the Day 03
ingestion output). Run the Day 03 ingest step first if the file is empty.

The Day 07 service (`Day  07/app/main.py`) is the production version
with RAG, the LangGraph agent, ChromaDB, and the full Streamlit UI.
