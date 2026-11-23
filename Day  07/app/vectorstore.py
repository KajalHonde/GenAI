
from pathlib import Path

import chromadb

from app.embed import generate_embeddings

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "chroma_db"

# Create the directory before initialising the client so the persistent
# store always has a valid path, including on Render's ephemeral filesystem.
DB_PATH.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(DB_PATH))

collection = client.get_or_create_collection(
    name="aapdamitra_documents",
    metadata={"hnsw:space": "cosine"}
)


def clear_collection():
    existing_data = collection.get()
    if existing_data["ids"]:
        collection.delete(ids=existing_data["ids"])
    print("Old collection data cleared.")


def add_documents(chunks):
    if not chunks:
        print("No chunks available.")
        return

    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts)

    start_id = collection.count()
    ids = [
        f"doc_{i}"
        for i in range(start_id, start_id + len(chunks))
    ]

    metadatas = []
    for chunk in chunks:
        metadatas.append({
            "source": chunk["source"],
            "title": chunk["title"],
            "page": str(chunk["page"]),
            "chunk_number": int(chunk["chunk_number"])
        })

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print(f"Successfully added {len(chunks)} chunks to ChromaDB.")


def search_documents(query, top_k=3):
    total = collection.count()

    if total == 0:
        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

    query_embedding = generate_embeddings([query])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=min(top_k, total)
    )

    return results
