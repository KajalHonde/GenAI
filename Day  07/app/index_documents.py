
"""Chunk, embed and index documents into ChromaDB."""

import argparse
from pathlib import Path

from app.chunking import load_and_chunk_documents
from app.embed import get_embedder
from app.vectorstore import AapdaMitraVectorStore


PROJECT_DIR = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--documents",
        default=str(PROJECT_DIR / "documents")
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=180
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=35
    )

    args = parser.parse_args()

    chunks = load_and_chunk_documents(
        args.documents,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )

    print("Total chunks:", len(chunks))

    if not chunks:
        print("No document chunks found. Check the documents folder.")
        return

    print("Loading embedding model...")

    embedder = get_embedder()

    store = AapdaMitraVectorStore()

    indexed = store.index_chunks(
        chunks,
        embedder,
        reset=True
    )

    print("Indexed chunks:", indexed)
    print("Collection:", store.collection_name)
    print("Database:", store.persist_directory)
    print("Total stored records:", store.count())


if __name__ == "__main__":
    main()
