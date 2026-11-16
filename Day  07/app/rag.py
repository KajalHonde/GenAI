
"""AapdaMitra Retrieval-Augmented Generation API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.vectorstore import search_documents
from app.llm import generate_response

router = APIRouter(tags=["RAG Question Answering"])

SYSTEM_PROMPT = """
You are AapdaMitra, a disaster-safety assistant.

Rules:
1. Answer using ONLY the supplied context.
2. Do not invent facts, emergency numbers, or instructions.
3. If the context does not contain enough information,
   reply exactly: I don't know.
4. Give clear, simple and practical answers.
5. Include citations using the source filename and page number.
6. Never invent a citation.
7. If information is missing, say: I don't know.
"""

# Maximum acceptable ChromaDB cosine distance.
MAX_DISTANCE = 0.40


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=3, ge=1, le=10)


def answer_question(question: str, top_k: int = 3):
    """Retrieve relevant chunks and generate a cited answer."""

    results = search_documents(question, top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    if not documents:
        return {
            "question": question,
            "answer": "I don't know.",
            "citations": []
        }

    # Reject weak or unrelated search results.
    best_distance = min(float(distance) for distance in distances)

    if best_distance > MAX_DISTANCE:
        return {
            "question": question,
            "answer": "I don't know.",
            "citations": []
        }

    context_parts = []
    citations = []

    for document, metadata in zip(documents, metadatas):
        source = metadata.get("source", "Unknown")
        page = metadata.get("page", "Not available")
        title = metadata.get("title", "Unknown")

        context_parts.append(
            f"Source: {source}\n"
            f"Title: {title}\n"
            f"Page: {page}\n"
            f"Content: {document}"
        )

        citation = {
            "source": source,
            "title": title,
            "page": page
        }

        if citation not in citations:
            citations.append(citation)

    context = "\n\n".join(context_parts)

    user_message = f"""
Question:
{question}

Retrieved context:
{context}

Answer using only the retrieved context.
Include source citations in your answer.
If the answer is not available, reply exactly:
I don't know.
"""

    try:
        answer = generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message
        )

        if not answer.strip():
            answer = "I don't know."

        if answer.strip().lower() == "i don't know.":
            citations = []

        return {
            "question": question,
            "answer": answer,
            "citations": citations
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Answer generation failed: {error}"
        )


@router.post("/ask")
def ask_question(request: AskRequest):
    return answer_question(
        request.question,
        request.top_k
    )
