
from app.retriever import retrieve_documents
from app.context_builder import build_context
from app.prompt import create_prompt

# User question
question = "What should we do during a flood?"

# Retrieve documents
documents = retrieve_documents(question)

# Build context
context = build_context(documents)

# Generate prompt
prompt = create_prompt(question, context)

print("\nGenerated Prompt:\n")
print(prompt)
