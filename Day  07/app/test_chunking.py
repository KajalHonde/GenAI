
from pathlib import Path

from app.chunking import create_chunks, load_documents

BASE_DIR = Path(__file__).resolve().parents[1]
DOCUMENTS_PATH = BASE_DIR / "documents"


def test_documents_are_loaded():
    documents = load_documents(DOCUMENTS_PATH)

    assert documents is not None
    assert len(documents) > 0


def test_chunks_are_created():
    documents = load_documents(DOCUMENTS_PATH)

    chunks = create_chunks(documents)

    assert chunks is not None
    assert len(chunks) > 0


def test_chunks_have_required_fields():
    documents = load_documents(DOCUMENTS_PATH)
    chunks = create_chunks(documents)

    required_fields = ["source", "title", "page", "chunk_number", "text"]

    for chunk in chunks:
        for field in required_fields:
            assert field in chunk


def test_chunk_text_is_not_empty():
    documents = load_documents(DOCUMENTS_PATH)
    chunks = create_chunks(documents)

    for chunk in chunks:
        assert chunk["text"].strip() != ""
