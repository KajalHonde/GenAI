
"""Persistent ChromaDB vector store."""

from pathlib import Path

import chromadb

from app.chunking import DocumentChunk


PROJECT_DIR = Path(__file__).resolve().parents[1]

CHROMA_DIR = PROJECT_DIR / "chroma_db"

COLLECTION_NAME = "aapdamitra_documents"


class AapdaMitraVectorStore:

    def __init__(self):
        CHROMA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        self.persist_directory = CHROMA_DIR

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        self.collection_name = COLLECTION_NAME

    def index_chunks(
        self,
        chunks: list[DocumentChunk],
        embedder,
        reset=False
    ):
        if reset:
            try:
                self.client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass

            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

        batch_size = 64
        indexed_count = 0

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]

            texts = [chunk.text for chunk in batch]
            embeddings = embedder.embed_documents(texts)

            self.collection.upsert(
                ids=[chunk.id for chunk in batch],
                documents=texts,
                embeddings=embeddings,
                metadatas=[
                    {
                        "source": chunk.source,
                        "page": chunk.page,
                        "title": chunk.title
                    }
                    for chunk in batch
                ]
            )

            indexed_count += len(batch)

        return indexed_count

    def search(self, query, embedder, top_k=5):
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if self.collection.count() == 0:
            return []

        query_embedding = embedder.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(
                top_k,
                self.collection.count()
            ),
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        output = []

        for index in range(len(results["ids"][0])):
            distance = results["distances"][0][index]

            output.append({
                "id": results["ids"][0][index],
                "text": results["documents"][0][index],
                "source": results["metadatas"][0][index]["source"],
                "page": results["metadatas"][0][index]["page"],
                "title": results["metadatas"][0][index]["title"],
                "similarity": round(1 - distance, 4)
            })

        return output

    def count(self):
        return self.collection.count()
