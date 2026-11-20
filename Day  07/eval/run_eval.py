
"""Evaluate two AapdaMitra RAG configurations."""

import json
from pathlib import Path

from app.chunking import create_chunks, load_documents
from app.rag import answer_question
from app.vectorstore import add_documents, clear_collection, search_documents

BASE_DIR = Path(__file__).resolve().parents[1]
DOCUMENTS_PATH = BASE_DIR / "documents"
EVAL_FILE = BASE_DIR / "eval" / "eval_set.json"
README_FILE = BASE_DIR / "README.md"

CONFIGURATIONS = [
    {"name": "Config A", "chunk_size": 100, "top_k": 3},
    {"name": "Config B", "chunk_size": 150, "top_k": 5}
]


def load_eval_questions():
    with open(EVAL_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_index(chunk_size):
    print(f"\nBuilding index with chunk size {chunk_size}...")

    documents = load_documents(DOCUMENTS_PATH)
    chunks = create_chunks(documents, chunk_size=chunk_size)

    clear_collection()
    add_documents(chunks)

    print(f"Indexed {len(chunks)} chunks.")


def evaluate_configuration(config, questions):
    correct = 0
    total = len(questions)
    q6_passed = False

    print(f"\nEvaluating {config['name']}...")

    for item in questions:
        question_id = item["id"]
        question = item["question"]
        expected_keywords = item["expected_keywords"]

        if question_id == "Q6":
            try:
                result = answer_question(question, config["top_k"])
                answer = result["answer"].strip().lower()

                passed = answer in ["i don't know", "i don't know."]
                q6_passed = passed
            except Exception as error:  # noqa: BLE001
                print(f"Q6 evaluation error: {error}")
                passed = False
                q6_passed = False

        else:
            results = search_documents(question, config["top_k"])
            retrieved_text = " ".join(
                results["documents"][0]
            ).lower()

            passed = any(
                keyword.lower() in retrieved_text
                for keyword in expected_keywords
            )

        if passed:
            correct += 1

        print(
            f"{question_id}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    score = (correct / total) * 100

    return {
        "name": config["name"],
        "chunk_size": config["chunk_size"],
        "top_k": config["top_k"],
        "correct": correct,
        "total": total,
        "score": score,
        "q6_passed": q6_passed
    }


def update_readme(results):
    winner = max(results, key=lambda item: item["score"])

    table = [
        "| Configuration | Chunk Size | Top-K | Score | Q6 Abstention |",
        "|---|---:|---:|---:|---|"
    ]

    for result in results:
        q6_status = "PASS" if result["q6_passed"] else "FAIL"

        table.append(
            f"| {result['name']} "
            f"| {result['chunk_size']} "
            f"| {result['top_k']} "
            f"| {result['correct']}/{result['total']} "
            f"({result['score']:.1f}%) "
            f"| {q6_status} |"
        )

    section = (
        "## RAG Evaluation Results\n\n"
        + "\n".join(table)
        + f"\n\n**Winner:** {winner['name']} "
        f"(Chunk Size: {winner['chunk_size']}, "
        f"Top-K: {winner['top_k']})\n"
    )

    if README_FILE.exists():
        readme_text = README_FILE.read_text(encoding="utf-8")
    else:
        readme_text = "# AapdaMitra\n"

    marker = "## RAG Evaluation Results"

    if marker in readme_text:
        readme_text = readme_text.split(marker)[0].rstrip() + "\n\n"

    readme_text += section

    README_FILE.write_text(readme_text, encoding="utf-8")
    print("\nREADME.md updated successfully.")


def main():
    questions = load_eval_questions()
    results = []

    print("Total evaluation questions:", len(questions))

    try:
        for config in CONFIGURATIONS:
            build_index(config["chunk_size"])
            result = evaluate_configuration(config, questions)
            results.append(result)

        update_readme(results)

        print("\n========== FINAL RESULTS ==========")

        for result in results:
            print(
                f"{result['name']}: "
                f"{result['correct']}/{result['total']} "
                f"({result['score']:.1f}%)"
            )

        winner = max(results, key=lambda item: item["score"])
        print("\nWinner:", winner["name"])

    finally:
        # Restore the normal Day 7 index.
        print("\nRestoring default chunk size 100...")
        build_index(100)
        print("Default index restored.")


if __name__ == "__main__":
    main()
