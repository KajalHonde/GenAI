
import re
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.llm import generate_response_with_usage
from app.observability import (
    INJECTION_REFUSAL,
    MAX_QUESTION_LENGTH,
    cache_get,
    cache_key,
    cache_set,
    is_prompt_injection,
    record_request,
)
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
    question: str = Field(
        ..., min_length=3, max_length=MAX_QUESTION_LENGTH
    )
    top_k: int = Field(default=5, ge=1, le=10)


def get_keywords(text):
    words = re.findall(r"[a-z]+", text.lower())

    return {
        word.removesuffix("s")
        for word in words
        if word not in STOP_WORDS and len(word) > 2
    }


def answer_question(
    question: str,
    top_k: int = 5,
    *,
    endpoint: str = "/ask",
    record: bool = True,
):
    """Answer a disaster-safety question with retrieval + generation.

    Production guards applied here so both ``/ask`` and the LangGraph agent
    share them: prompt-injection refusal, an answer cache, and per-request
    logging of latency and token usage.
    """

    start = time.perf_counter()

    # Prompt-injection guard: refuse before the model sees the input.
    if is_prompt_injection(question):
        latency = (time.perf_counter() - start) * 1000
        if record:
            record_request(
                endpoint, latency, blocked=True, status="blocked"
            )
        return {
            "question": question,
            "answer": INJECTION_REFUSAL,
            "citations": []
        }

    # Cache lookup keyed on the normalised question and top_k.
    key = cache_key(question, top_k)
    cached = cache_get(key)
    if cached is not None:
        latency = (time.perf_counter() - start) * 1000
        if record:
            record_request(endpoint, latency, cached=True, status="ok")
        return cached

    results = search_documents(question, top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    def _abstain():
        latency = (time.perf_counter() - start) * 1000
        if record:
            record_request(endpoint, latency, status="ok")
        result = {
            "question": question,
            "answer": "I don't know.",
            "citations": []
        }
        cache_set(key, result)
        return result

    if not documents:
        return _abstain()

    relevant_chunks = []

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):

        if float(distance) <= MAX_DISTANCE:
            relevant_chunks.append((document, metadata))

    if not relevant_chunks:
        return _abstain()

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

        response = generate_response_with_usage(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message
        )

        answer = response["answer"]
        usage = response["usage"]

    except Exception as error:  # noqa: BLE001

        latency = (time.perf_counter() - start) * 1000
        if record:
            record_request(endpoint, latency, status="error")
        raise HTTPException(
            status_code=500,
            detail=f"Answer generation failed: {error}"
        )

    if not answer or answer.strip().lower() == "i don't know.":
        answer = "I don't know."
        citations = []

    latency = (time.perf_counter() - start) * 1000
    if record:
        record_request(
            endpoint,
            latency,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            status="ok"
        )

    result = {
        "question": question,
        "answer": answer,
        "citations": citations
    }

    cache_set(key, result)
    return result


@router.post("/ask")
def ask_question(request: AskRequest):

    return answer_question(
        request.question,
        request.top_k,
        endpoint="/ask"
    )
