
from fastapi import FastAPI, Query, HTTPException

from app.vectorstore import search_documents


app = FastAPI(
    title="AapdaMitra Semantic Search API",
    version="1.0.0"
)


@app.get("/")
def home():

    return {
        "message": "Welcome to AapdaMitra Semantic Search API"
    }


@app.get("/search/semantic")
def semantic_search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(3, ge=1, le=10)
):

    # Search relevant documents in ChromaDB

    results = search_documents(q, top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    search_results = []

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):

        search_results.append({
            "text": document,
            "source": metadata["source"],
            "title": metadata["title"],
            "page": metadata["page"],
            "chunk_number": metadata["chunk_number"],
            "distance": round(distance, 4)
        })

    return {
        "query": q,
        "total_results": len(search_results),
        "results": search_results
    }
