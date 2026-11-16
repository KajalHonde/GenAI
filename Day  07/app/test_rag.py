from app.rag_pipeline import generate_rag_answer


question = "What should we do during a flood?"

print("\nGenerating answer using LLM...\n")

answer = generate_rag_answer(question)

print("\nAapdaMitra Final Answer:\n")
print(answer)