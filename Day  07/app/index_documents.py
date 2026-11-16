
from app.chunking import load_documents
from app.vectorstore import add_documents


def index_all_documents():

    # Load document chunks
    documents = load_documents()

    print("Total chunks:", len(documents))

    # Store chunks in ChromaDB
    add_documents(documents)


if __name__ == "__main__":
    index_all_documents()
