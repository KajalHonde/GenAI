
"""AapdaMitra API."""

from fastapi import FastAPI
from app.search_api import router as search_router
from app.rag import router as rag_router

app = FastAPI(
    title="AapdaMitra API",
    description="Disaster safety semantic search and RAG question answering.",
    version="1.0.0"
)

# Existing semantic search API
app.include_router(search_router)

# New RAG question-answering API
app.include_router(rag_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AapdaMitra API",
        "health": "/health",
        "semantic_search": "/search/semantic?q=earthquake safety",
        "ask": "/ask",
        "documentation": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}
