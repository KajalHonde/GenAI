from app.retriever import retrieve_documents
from app.context_builder import build_context
from app.prompt import create_prompt
from app.llm import generate_response


def generate_rag_answer(question):

    # Step 1: Retrieve relevant documents
    documents = retrieve_documents(question)

    # Step 2: Build context from retrieved documents
    context = build_context(documents)

    # Step 3: Create prompt
    prompt = create_prompt(question, context)

    # Step 4: Give instructions to the LLM
    system_prompt = """
    You are AapdaMitra, a disaster management assistant.

    Answer the user's question using only the provided context.

    Give simple, clear and safety-related answers.
    Do not make up information.

    If information is unavailable, say:
    I don't have enough information to answer this question.
    """

    # Step 5: Generate final answer using LLM
    answer = generate_response(
        system_prompt=system_prompt,
        user_message=prompt
    )

    return answer