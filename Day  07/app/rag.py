
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.llm import generate_response
from app.vectorstore import search_documents

router = APIRouter(tags=["RAG Question Answering"])

SYSTEM_PROMPT = """
You are AapdaMitra, a disaster-safety assistant.

Rules:
1. Answer using only the supplied context.
2. Never invent facts or safety instructions.
3. If relevant information is available, answer using it.
4. If information is incomplete, mention the limitation.
5. Give simple and practical answers.
6. Never invent citations.
"""

MAX_DISTANCE = 0.55

STOP_WORDS = {
    "what", "should", "people", "do", "during", "when",
    "are", "is", "the", "a", "an", "how", "can", "to",
    "for", "in", "on", "they", "their", "and", "or",
    "be", "stay", "safe", "take", "does", "of", "from"
}


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)


def get_keywords(text):
    words = re.findall(r"[a-z]+", text.lower())

    return {
        word.removesuffix("s")
        for word in words
        if word not in STOP_WORDS and len(word) > 2
    }


def answer_question(question: str, top_k: int = 5):

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

    relevant_chunks = []

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):

        if float(distance) <= MAX_DISTANCE:
            relevant_chunks.append((document, metadata))

    if not relevant_chunks:
        return {
            "question": question,
            "answer": "I don't know.",
            "citations": []
        }

    question_keywords = get_keywords(question)

    context_parts = []
    citations = []

    for document, metadata in relevant_chunks:

        source = metadata.get("source", "Unknown")
        title = metadata.get("title", "Unknown")
        page = metadata.get("page", "Not available")

        context_parts.append(
            f"""
Source: {source}
Title: {title}
Page: {page}
Information: {document}
"""
        )

        # Add a citation only when its title matches
        # the main topic of the user's question.
        title_keywords = get_keywords(title)

        if question_keywords.intersection(title_keywords):

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

Available context:
{context}

Answer the question using only relevant information
from the available context.

Do not invent safety instructions.
"""

    try:

        answer = generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message
        )

        if not answer or answer.strip().lower() == "i don't know.":
            answer = "I don't know."
            citations = []

        return {
            "question": question,
            "answer": answer,
            "citations": citations
        }

    except Exception as error:  # noqa: BLE001

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
