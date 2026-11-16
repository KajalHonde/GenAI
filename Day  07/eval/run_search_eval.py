
from pathlib import Path

from app.chunking import load_documents
from app.embed import semantic_search


# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent

QUESTIONS_FILE = BASE_DIR / "eval" / "questions.txt"
RESULTS_FILE = BASE_DIR / "eval" / "search_results.md"


def run_evaluation():

    # Load document chunks
    documents = load_documents()

    # Read questions
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = [
            line.strip()
            for line in file
            if line.strip()
        ]

    # Store search results
    with open(RESULTS_FILE, "w", encoding="utf-8") as file:

        file.write("# Semantic Search Evaluation\n\n")

        for number, question in enumerate(questions, start=1):

            file.write(f"## Question {number}: {question}\n\n")

            results = semantic_search(
                question,
                documents,
                top_k=3
            )

            for rank, result in enumerate(results, start=1):

                file.write(f"### Result {rank}\n\n")
                file.write(f"**Source:** {result['metadata']['source']}\n\n")
                file.write(f"**Page:** {result['metadata']['page']}\n\n")
                file.write(f"**Title:** {result['metadata']['title']}\n\n")
                file.write(f"**Score:** {result['score']:.4f}\n\n")
                file.write(f"**Text:** {result['text']}\n\n")

            file.write("---\n\n")

    print("Evaluation completed!")
    print("Total questions:", len(questions))
    print("Results saved to:", RESULTS_FILE)


if __name__ == "__main__":
    run_evaluation()
