"""Embedding helper for AapdaMitra.

Uses ChromaDB's built-in ONNX embedding function (all-MiniLM-L6-v2 via
onnxruntime) instead of sentence-transformers + PyTorch.  This keeps the
runtime footprint under ~150 MB so the service runs on Render's free tier.
The model is downloaded once on first use and cached in the directory set
by SENTENCE_TRANSFORMERS_HOME / HF_HOME (or ~/.cache by default).
"""

from __future__ import annotations

import numpy as np
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

# Lazy singleton — avoids downloading the model at import time.
_ef = None


def _get_ef() -> ONNXMiniLM_L6_V2:
    global _ef
    if _ef is None:
        _ef = ONNXMiniLM_L6_V2()
    return _ef


def generate_embeddings(texts: list[str]) -> np.ndarray:
    """Return a float32 numpy array of shape (len(texts), 384)."""
    ef = _get_ef()
    # ChromaDB embedding functions return a list of lists.
    result = ef(texts)
    return np.array(result, dtype=np.float32)


def semantic_search(question: str, documents: list[dict], top_k: int = 3) -> list[dict]:
    """Find the most relevant document chunks for a question."""
    if not documents:
        return []

    texts = [doc["text"] for doc in documents]
    doc_embeddings = generate_embeddings(texts)
    q_embedding = generate_embeddings([question])[0]

    scores = np.dot(doc_embeddings, q_embedding)
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {
            "text": documents[i]["text"],
            "metadata": documents[i]["metadata"],
            "score": float(scores[i]),
        }
        for i in top_indices
    ]
