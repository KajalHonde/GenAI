
from unittest.mock import patch

from app.retriever import retrieve_documents


def test_retrieve_documents_returns_list():
    mock_results = {
        "documents": [["Flood safety information", "Emergency contact details"]]
    }

    with patch(
        "app.retriever.generate_embeddings", return_value=[[0.1, 0.2]]
    ), patch("app.retriever.collection.query", return_value=mock_results):
        documents = retrieve_documents("What should we do during a flood?")

    assert isinstance(documents, list)


def test_retrieve_documents_returns_relevant_documents():
    expected_documents = [
        "Flood safety information",
        "Emergency contact details",
        "Evacuation guidelines"
    ]

    mock_results = {
        "documents": [expected_documents]
    }

    with patch(
        "app.retriever.generate_embeddings", return_value=[[0.1, 0.2]]
    ), patch("app.retriever.collection.query", return_value=mock_results):
        documents = retrieve_documents("What should we do during a flood?")

    assert documents == expected_documents


def test_retrieve_documents_searches_three_results():
    mock_results = {
        "documents": [["Flood safety information"]]
    }

    with patch(
        "app.retriever.generate_embeddings", return_value=[[0.1, 0.2]]
    ), patch(
        "app.retriever.collection.query", return_value=mock_results
    ) as mock_query:
        retrieve_documents("What should we do during a flood?")

    mock_query.assert_called_once_with(
        query_embeddings=[[0.1, 0.2]],
        n_results=3
    )
