
"""Run semantic search evaluation for AapdaMitra."""

from pathlib import Path

from app.vectorstore import search_documents

# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[1]
QUESTIONS_FILE = PROJECT_DIR / "eval" / "questions.txt"
RESULTS_FILE = PROJECT_DIR / "eval" / "search_results.md"

TOP_K = 3


def run_evaluation():
    if not QUESTIONS_FILE.exists():
        print(f"Questions file not found: {QUESTIONS_FILE}")
        return

    # Read the 10 evaluation questions
    questions = [
        line.strip()
        for line in QUESTIONS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if not questions:
        print("No questions found in eval/questions.txt")
        return

    output = [
        "# AapdaMitra Semantic Search Evaluation",
        "",
        f"Total questions: {len(questions)}",
        f"Results per question: {TOP_K}",
        "",
    ]

    for number, question in enumerate(questions, start=1):
        print(f"Evaluating question {number}/{len(questions)}: {question}")

        output.extend([
            f"## Question {number}: {question}",
            "",
        ])

        try:
            results = search_documents(question, TOP_K)

            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

            if not documents:
                output.extend(["No results found.", ""])
                continue

            for rank, (document, metadata, distance) in enumerate(
                zip(documents, metadatas, distances), start=1
            ):
                output.extend([
                    f"### Result {rank}",
                    f"- **Source:** {metadata.get('source', 'Unknown')}",
                    f"- **Title:** {metadata.get('title', 'Unknown')}",
                    f"- **Page:** {metadata.get('page', 'Unknown')}",
                    f"- **Chunk:** {metadata.get('chunk_number', 'Unknown')}",
                    f"- **Distance:** {float(distance):.4f}",
                    "",
                    "**Matched text:**",
                    "",
                    str(document),
                    "",
                ])

        except Exception as error:  # noqa: BLE001
            output.extend([
                f"Search failed: {error}",
                "",
            ])
            print(f"Error: {error}")

    RESULTS_FILE.write_text("\n".join(output), encoding="utf-8")

    print("\nEvaluation completed!")
    print(f"Questions evaluated: {len(questions)}")
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    run_evaluation()
