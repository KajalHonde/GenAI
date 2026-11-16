
from app.embed import generate_embeddings
from app.vectorstore import collection


def search_documents(query):

    # Convert question into embedding
    query_embedding = generate_embeddings([query])

    # Search in ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )

    print("\nRelevant Documents:\n")

    for i, document in enumerate(results["documents"][0]):

        print("Result:", i + 1)
        print("Document:", document)
        print("Metadata:", results["metadatas"][0][i])
        print("--------------------------------")


if __name__ == "__main__":

    question = input("Enter your question: ")

    search_documents(question)
