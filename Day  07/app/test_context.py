
from app import retriever
from app.context_builder import build_context


class FakeCollection:
    def query(self, **kwargs):
        return {
            "documents": [
                [
                    "During a flood, move to higher ground.",
                    "Follow instructions from local authorities."
                ]
            ]
        }


def get_fake_documents(monkeypatch):
    monkeypatch.setattr(
        retriever,
        "generate_embeddings",
        lambda texts: [[0.1, 0.2]]
    )

    monkeypatch.setattr(
        retriever,
        "collection",
        FakeCollection()
    )

    return retriever.retrieve_documents(
        "What should we do during a flood?"
    )


def test_retrieve_documents_returns_results(monkeypatch):
    documents = get_fake_documents(monkeypatch)

    assert documents is not None
    assert len(documents) > 0


def test_build_context_returns_text(monkeypatch):
    documents = get_fake_documents(monkeypatch)

    context = build_context(documents)

    assert context is not None
    assert isinstance(context, str)
    assert len(context.strip()) > 0


def test_context_contains_retrieved_information(monkeypatch):
    documents = get_fake_documents(monkeypatch)

    context = build_context(documents)

    assert "higher ground" in context
    assert "local authorities" in context
