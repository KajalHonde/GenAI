
"""AapdaMitra Semantic Search API."""

from fastapi import FastAPI

from app.semantic_routes import router as semantic_router


app = FastAPI(
    title="AapdaMitra Semantic Search API",
    description="Semantic search for disaster safety documents.",
    version="1.0.0"
)

app.include_router(semantic_router)


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
