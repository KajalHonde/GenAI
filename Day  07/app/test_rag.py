
from unittest.mock import patch

from app.rag_pipeline import generate_rag_answer


def test_generate_rag_answer_returns_text():
    with patch(
        "app.rag_pipeline.retrieve_documents",
        return_value=["Flood safety information"],
    ), patch(
        "app.rag_pipeline.build_context", return_value="Flood safety context"
    ), patch(
        "app.rag_pipeline.create_prompt",
        return_value="Flood question and context",
    ), patch(
        "app.rag_pipeline.generate_response",
        return_value="Move to higher ground.",
    ):

        answer = generate_rag_answer("What should we do during a flood?")

    assert isinstance(answer, str)
    assert len(answer) > 0


def test_generate_rag_answer_returns_llm_response():
    expected_answer = "Move to higher ground during a flood."

    with patch(
        "app.rag_pipeline.retrieve_documents",
        return_value=["Flood information"],
    ), patch(
        "app.rag_pipeline.build_context", return_value="Flood context"
    ), patch(
        "app.rag_pipeline.create_prompt", return_value="Flood prompt"
    ), patch(
        "app.rag_pipeline.generate_response", return_value=expected_answer
    ):
        answer = generate_rag_answer("What should we do during a flood?")

    assert answer == expected_answer


def test_generate_rag_answer_uses_question():
    question = "What should we do during a flood?"

    with patch(
        "app.rag_pipeline.retrieve_documents", return_value=[]
    ) as mock_retrieve, patch(
        "app.rag_pipeline.build_context", return_value=""
    ), patch(
        "app.rag_pipeline.create_prompt", return_value="Prompt"
    ), patch(
        "app.rag_pipeline.generate_response", return_value="Stay safe."
    ):
        generate_rag_answer(question)

    mock_retrieve.assert_called_once_with(question)
