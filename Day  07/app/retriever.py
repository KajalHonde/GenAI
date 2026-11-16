
from app.embed import generate_embeddings
from app.vectorstore import collection


def retrieve_documents(query):

    # Convert question into embedding
    query_embedding = generate_embeddings([query])

    # Search relevant documents
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )

    # Return retrieved documents
    documents = results["documents"][0]

    return documents
