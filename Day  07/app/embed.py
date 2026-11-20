
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts):
    """
    Convert a list of text into numerical vectors.
    """
    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    return embeddings


def semantic_search(question, documents, top_k=3):
    """
    Find the most relevant document chunks for a question.
    """

    if not documents:
        return []

    # Extract text from document chunks
    texts = [doc["text"] for doc in documents]

    # Generate document embeddings
    document_embeddings = generate_embeddings(texts)

    # Generate question embedding
    question_embedding = generate_embeddings([question])[0]

    # Calculate similarity scores
    scores = np.dot(document_embeddings, question_embedding)

    # Get the highest scoring results
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in top_indices:
        result = {
            "text": documents[index]["text"],
            "metadata": documents[index]["metadata"],
            "score": float(scores[index])
        }

        results.append(result)

    return results


if __name__ == "__main__":
    from app.chunking import load_documents

    documents = load_documents()

    print("Total documents chunks:", len(documents))

    question = "What should we do during floods?"

    results = semantic_search(question, documents)

    print("\nQuestion:", question)

    for result in results:
        print("\nRelevant text:", result["text"])
        print("Metadata:", result["metadata"])
        print("Similarity score:", result["score"])
