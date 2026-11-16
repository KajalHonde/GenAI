
import chromadb
from pathlib import Path

from app.embed import generate_embeddings


# Create persistent ChromaDB folder
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

# Create collection
collection = client.get_or_create_collection(
    name="aapdamitra_documents"
)


def add_documents(documents):

    texts = [doc["text"] for doc in documents]

    embeddings = generate_embeddings(texts)

    ids = [doc["id"] for doc in documents]

    metadatas = [
        doc["metadata"] for doc in documents
    ]

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("Documents added successfully!")


def search_documents(question, top_k=3):

    question_embedding = generate_embeddings(
        [question]
    )[0]

    results = collection.query(
        query_embeddings=[
            question_embedding.tolist()
        ],
        n_results=top_k
    )

    return results
