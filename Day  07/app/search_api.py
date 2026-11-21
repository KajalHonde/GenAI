
"""AapdaMitra Semantic Search API Router."""

import time

from fastapi import APIRouter, HTTPException, Query

from app.observability import MAX_QUERY_LENGTH, record_request
from app.vectorstore import search_documents

router = APIRouter(tags=["Semantic Search"])


@router.get("/search/semantic")
def semantic_search(
    q: str = Query(
        ...,
        min_length=1,
        max_length=MAX_QUERY_LENGTH,
        description="Enter your disaster-related question"
    ),
    top_k: int = Query(
        3,
        ge=1,
        le=10,
        description="Number of relevant results"
    )
):
    start = time.perf_counter()

    try:
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
                "distance": round(float(distance), 4)
            })

        latency = (time.perf_counter() - start) * 1000
        record_request("/search/semantic", latency, status="ok")

        return {
            "query": q,
            "total_results": len(search_results),
            "results": search_results
        }

    except Exception as error:  # noqa: BLE001
        latency = (time.perf_counter() - start) * 1000
        record_request("/search/semantic", latency, status="error")
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {error}"
        )
