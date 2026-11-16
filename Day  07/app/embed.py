
"""Create text embeddings using Sentence Transformers."""

import os
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


class TextEmbedder:

    def __init__(self, model_name=None):
        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.model = SentenceTransformer(self.model_name)

    def embed_documents(self, texts):
        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return np.asarray(
            vectors,
            dtype=np.float32
        ).tolist()

    def embed_query(self, query):
        vector = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )[0]

        return np.asarray(
            vector,
            dtype=np.float32
        ).tolist()


@lru_cache(maxsize=1)
def get_embedder():
    """Load the embedding model once."""
    return TextEmbedder()
