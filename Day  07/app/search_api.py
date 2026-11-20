
"""AapdaMitra Semantic Search API Router."""

from fastapi import APIRouter, HTTPException, Query

from app.vectorstore import search_documents

router = APIRouter(tags=["Semantic Search"])


@router.get("/search/semantic")
def semantic_search(
    q: str = Query(
        ...,
        min_length=1,
        description="Enter your disaster-related question"
    ),
    top_k: int = Query(
        3,
        ge=1,
        le=10,
        description="Number of relevant results"
    )
):
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

        return {
            "query": q,
            "total_results": len(search_results),
            "results": search_results
        }

    except Exception as error:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {error}"
        )
