
from pathlib import Path

from app.chunking import create_chunks, load_documents
from app.vectorstore import add_documents, clear_collection

BASE_DIR = Path(__file__).resolve().parents[1]

DOCUMENTS_PATH = BASE_DIR / "documents"


def index_documents():

    print("Loading documents...")

    documents = load_documents(DOCUMENTS_PATH)

    print("Total documents:", len(documents))

    print("\nCreating chunks...")

    chunks = create_chunks(documents)

    print("Total chunks:", len(chunks))

    if not chunks:
        print("No documents found.")
        return

    print("\nClearing old index...")

    clear_collection()

    print("\nIndexing documents...")

    add_documents(chunks)

    print("\nIndexing completed successfully!")


if __name__ == "__main__":
    index_documents()
