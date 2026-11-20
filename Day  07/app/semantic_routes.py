
"""Semantic search API route."""

from fastapi import APIRouter, HTTPException, Query

from app.embed import get_embedder
from app.vectorstore import AapdaMitraVectorStore

router = APIRouter(tags=["Semantic Search"])


@router.get("/search/semantic")
def semantic_search(
    q: str = Query(
        ...,
        min_length=1,
        description="Enter your disaster-related question"
    ),
    top_k: int = Query(
        5,
        ge=1,
        le=20
    )
):
    try:
        store = AapdaMitraVectorStore()

        if store.count() == 0:
            raise HTTPException(
                status_code=503,
                detail="No documents indexed. Run app.index_documents first."
            )

        results = store.search(
            q,
            get_embedder(),
            top_k=top_k
        )

        return {
            "query": q,
            "count": len(results),
            "results": results
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {error}"
        )
