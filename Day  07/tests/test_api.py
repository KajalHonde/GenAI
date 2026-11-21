from unittest.mock import patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.tools import heat_risk_index
from app.vectorstore import add_documents

client = TestClient(app)


def test_add_documents_stores_chunk_records():
    chunks = [
        {
            "text": "Move to higher ground.",
            "source": "flood.pdf",
            "title": "Flood Safety",
            "page": 2,
            "chunk_number": 4,
        }
    ]

    with patch("app.vectorstore.collection.count", return_value=3), patch(
        "app.vectorstore.generate_embeddings",
        return_value=np.array([[0.1, 0.2]]),
    ), patch("app.vectorstore.collection.add") as add:
        add_documents(chunks)

    add.assert_called_once_with(
        ids=["doc_3"],
        documents=["Move to higher ground."],
        embeddings=[[0.1, 0.2]],
        metadatas=[
            {
                "source": "flood.pdf",
                "title": "Flood Safety",
                "page": "2",
                "chunk_number": 4,
            }
        ],
    )


def test_add_documents_skips_empty_records():
    with patch("app.vectorstore.generate_embeddings") as embed, patch(
        "app.vectorstore.collection.add"
    ) as add:
        add_documents([])

    embed.assert_not_called()
    add.assert_not_called()


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_semantic_search_returns_formatted_records():
    results = {
        "documents": [["Move to higher ground."]],
        "metadatas": [[
            {
                "source": "flood.pdf",
                "title": "Flood Safety",
                "page": "2",
                "chunk_number": 4,
            }
        ]],
        "distances": [[0.123456]],
    }

    with patch("app.search_api.search_documents", return_value=results):
        response = client.get("/search/semantic", params={"q": "flood safety"})

    assert response.status_code == 200
    assert response.json() == {
        "query": "flood safety",
        "total_results": 1,
        "results": [
            {
                "text": "Move to higher ground.",
                "source": "flood.pdf",
                "title": "Flood Safety",
                "page": "2",
                "chunk_number": 4,
                "distance": 0.1235,
            }
        ],
    }


def test_semantic_search_returns_no_records_for_empty_index():
    results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    with patch("app.search_api.search_documents", return_value=results):
        response = client.get("/search/semantic", params={"q": "flood safety"})

    assert response.status_code == 200
    assert response.json()["total_results"] == 0
    assert response.json()["results"] == []


def test_semantic_search_rejects_empty_query():
    response = client.get("/search/semantic", params={"q": ""})

    assert response.status_code == 422


def test_ask_endpoint_uses_fake_llm_and_returns_citation():
    search_results = {
        "documents": [["Move to higher ground during a flood."]],
        "metadatas": [[
            {"source": "flood.pdf", "title": "Flood Safety", "page": "2"}
        ]],
        "distances": [[0.1]],
    }
    expected_answer = "Move to higher ground."

    with patch("app.rag.search_documents", return_value=search_results), patch(
        "app.rag.generate_response_with_usage",
        return_value={
            "answer": expected_answer,
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
        },
    ) as generate:
        response = client.post(
            "/ask",
            json={"question": "What should I do during a flood?"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "question": "What should I do during a flood?",
        "answer": expected_answer,
        "citations": [
            {"source": "flood.pdf", "title": "Flood Safety", "page": "2"}
        ],
    }
    generate.assert_called_once()


def test_ask_endpoint_abstains_when_no_records_are_found():
    search_results = {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    with patch(
        "app.rag.search_documents", return_value=search_results
    ), patch("app.rag.generate_response_with_usage") as generate:
        response = client.post(
            "/ask",
            json={"question": "What should I do during a flood?"},
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "I don't know."
    assert response.json()["citations"] == []
    generate.assert_not_called()


def test_heat_risk_agent_tool_returns_calculation():
    result = heat_risk_index(40, 60)

    assert result["temperature_c"] == 40
    assert result["humidity"] == 60
    assert result["feels_like_c"] > 40
    assert result["risk_level"] == "danger"
    assert result["advice"]


@pytest.mark.parametrize(
    ("temperature", "humidity"),
    [(61, 50), (25, 101)],
)
def test_heat_risk_agent_tool_rejects_out_of_range_inputs(
    temperature, humidity
):
    with pytest.raises(ValueError):
        heat_risk_index(temperature, humidity)


def test_agent_endpoint_returns_agent_result():
    agent_result = {
        "decision": "HEAT",
        "result": {"heat_risk": {"risk_level": "danger"}},
    }

    with patch("app.main.run_agent", return_value=agent_result) as run_agent:
        response = client.post(
            "/agent",
            json={"question": "Calculate heat risk at 40 C and 60% humidity"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["decision"] == "HEAT"
    assert response.json()["result"] == agent_result["result"]
    run_agent.assert_called_once()
