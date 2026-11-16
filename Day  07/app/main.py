
"""AapdaMitra Semantic Search API."""

from fastapi import FastAPI

from app.search_api import router as search_router


app = FastAPI(
    title="AapdaMitra Semantic Search API",
    description="Semantic search for disaster safety documents.",
    version="1.0.0"
)

# Register semantic search API
app.include_router(search_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AapdaMitra Semantic Search API",
        "health": "/health",
        "semantic_search": "/search/semantic?q=earthquake safety",
        "documentation": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
