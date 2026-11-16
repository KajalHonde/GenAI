
from app.retriever import retrieve_documents
from app.context_builder import build_context

# User question
question = "What should we do during a flood?"

# Retrieve relevant documents
documents = retrieve_documents(question)

# Build context
context = build_context(documents)

print("\nFinal Context:\n")
print(context)
