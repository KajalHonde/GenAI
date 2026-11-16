
from pathlib import Path

from app.vectorstore import search_documents


questions = [
    "What should we do before a flood?",
    "What precautions should we take during a flood?",
    "What should we do after a flood?",
    "How can we prepare our home for flooding?",
    "Which essential items should be moved to an upper floor?",
    "What should we do when flash flooding is possible?",
    "Is it safe to drive through flooded roads?",
    "How can we get flood warnings and updates?",
    "How can we protect electrical equipment during floods?",
    "What precautions should we take while walking through floodwater?"
]


BASE_DIR = Path(__file__).resolve().parents[1]

EVAL_DIR = BASE_DIR / "eval"

EVAL_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = EVAL_DIR / "search_results.md"

results_text = "# AapdaMitra Semantic Search Evaluation\n\n"

results_text += "Total questions: 10\n\n"


for i, question in enumerate(questions, start=1):

    print(f"\nQuestion {i}: {question}")

    results = search_documents(question, top_k=3)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    results_text += f"## Question {i}: {question}\n\n"

    for j, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances), start=1
    ):

        print(f"\nHit {j}")
        print("Source:", metadata["source"])
        print("Title:", metadata["title"])
        print("Distance:", round(distance, 4))
        print("Text:", document[:150])

        results_text += f"### Hit {j}\n\n"
        results_text += f"- Source: {metadata['source']}\n"
        results_text += f"- Title: {metadata['title']}\n"
        results_text += f"- Page: {metadata['page']}\n"
        results_text += f"- Chunk: {metadata['chunk_number']}\n"
        results_text += f"- Distance: {distance:.4f}\n"
        results_text += f"- Text: {document[:300]}\n\n"

    results_text += "---\n\n"


with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write(results_text)


print("\nSemantic search evaluation completed!")

print("Results saved at:", OUTPUT_FILE)
