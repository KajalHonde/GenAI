"""Measure AapdaMitra production metrics: latency, tokens and cache.

Runs a handful of real questions through the RAG pipeline and prints the
per-request latency and token usage, then repeats one question to show the
cache benefit. The numbers feed the 'Production notes' section of the README.

Run from the Day 07 directory::

    python -m eval.bench_production
"""

import time

from app.observability import metrics_clear, metrics_last, metrics_summary
from app.rag import answer_question
from app.vectorstore import collection

QUESTIONS = [
    "What should I do before a flood?",
    "What precautions should we take during a heatwave?",
    "What should people do during an earthquake?",
    "Is it safe to drive through flooded roads?",
]


def ensure_index():
    """Build the default index if the vector store is empty."""
    if collection.count() > 0:
        return

    from app.chunking import create_chunks, load_documents
    from app.vectorstore import add_documents

    print("Index empty - building default index (chunk size 100)...")
    documents = load_documents("documents")
    chunks = create_chunks(documents, chunk_size=100)
    add_documents(chunks)


def run_one(question):
    start = time.perf_counter()
    result = answer_question(question, top_k=5)
    latency_ms = (time.perf_counter() - start) * 1000

    last = metrics_last()
    tokens = (
        last["prompt_tokens"] + last["completion_tokens"]
        if last else 0
    )
    cached = bool(last and last["cached"])

    return result, latency_ms, tokens, cached


def main():
    metrics_clear()
    ensure_index()

    print("\n=== AapdaMitra production benchmark ===\n")
    header = (
        f"{'#':<3}{'cached':<8}{'latency_ms':>12}{'tokens':>8}  question"
    )
    print(header)
    print("-" * len(header))

    for index, question in enumerate(QUESTIONS, start=1):
        _result, latency_ms, tokens, cached = run_one(question)
        print(
            f"{index:<3}{'no':<8}{latency_ms:>12.1f}{tokens:>8}  {question}"
        )

    # Repeat the first question: it should be served from the cache.
    _result, latency_ms, tokens, cached = run_one(QUESTIONS[0])
    label = "yes" if cached else "no"
    print(
        f"{'+':<3}{label:<8}{latency_ms:>12.1f}{tokens:>8}  "
        f"{QUESTIONS[0]} (repeat)"
    )

    summary = metrics_summary()

    print("\n=== Aggregated metrics (from /metrics) ===")
    print(f"total_requests : {summary['total_requests']}")
    print(f"avg_latency_ms : {summary['avg_latency_ms']}")
    print(f"p95_latency_ms : {summary['p95_latency_ms']}")
    print(f"total_tokens   : {summary['total_tokens']}")
    print(f"cache_hits     : {summary['cache_hits']}")
    print(f"cache_hit_rate : {summary['cache_hit_rate']}")
    print(f"blocked_reqs   : {summary['blocked_requests']}")

    ask = summary["by_endpoint"].get("/ask", {})
    if ask:
        print("\n/ask endpoint:")
        print(f"  requests      : {ask['requests']}")
        print(f"  avg_latency_ms: {ask['avg_latency_ms']}")
        print(f"  tokens        : {ask['tokens']}")
        print(f"  cache_hits    : {ask['cache_hits']}")


if __name__ == "__main__":
    main()
