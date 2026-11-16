
from app.retriever import retrieve_documents

question = "What should we do during a flood?"

documents = retrieve_documents(question)

print("\nRetrieved Documents:\n")

for i, document in enumerate(documents):

    print("Document:", i + 1)
    print(document)
    print("----------------------")
