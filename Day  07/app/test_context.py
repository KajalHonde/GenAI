
from app.context_builder import build_context
from app.retriever import retrieve_documents


def test_retrieve_documents_returns_results():
    question = "What should we do during a flood?"

    documents = retrieve_documents(question)

    assert documents is not None
    assert len(documents) > 0


def test_build_context_returns_text():
    question = "What should we do during a flood?"

    documents = retrieve_documents(question)
    context = build_context(documents)

    assert context is not None
    assert isinstance(context, str)
    assert len(context.strip()) > 0


def test_context_contains_retrieved_information():
    question = "What should we do during a flood?"

    documents = retrieve_documents(question)
    context = build_context(documents)

    assert len(context.strip()) > 0
