
from unittest.mock import patch

import numpy as np

from app.vectorstore import search_documents


def test_search_documents_returns_empty_results_when_collection_is_empty():

    with patch("app.vectorstore.collection.count", return_value=0):

        results = search_documents(
            "What should we do during a flood?"
        )

    assert results == {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    }


def test_search_documents_returns_results():

    mock_results = {
        "documents": [["Flood safety information"]],
        "metadatas": [[
            {"source": "flood.pdf", "title": "Flood Safety"}
        ]],
        "distances": [[0.15]]
    }

    mock_embedding = np.array([[0.1, 0.2]])

    with patch("app.vectorstore.collection.count", return_value=5), patch(
        "app.vectorstore.generate_embeddings",
        return_value=mock_embedding
    ), patch(
        "app.vectorstore.collection.query",
        return_value=mock_results
    ):

        results = search_documents(
            "What should we do during a flood?"
        )

    assert results == mock_results


def test_search_documents_limits_top_k_to_collection_count():

    mock_results = {
        "documents": [["Flood information"]],
        "metadatas": [[{"source": "flood.pdf"}]],
        "distances": [[0.2]]
    }

    mock_embedding = np.array([[0.1, 0.2]])

    with patch("app.vectorstore.collection.count", return_value=1), patch(
        "app.vectorstore.generate_embeddings",
        return_value=mock_embedding
    ), patch(
        "app.vectorstore.collection.query",
        return_value=mock_results
    ) as mock_query:

        search_documents("Flood safety", top_k=3)

        mock_query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2]],
            n_results=1
        )
