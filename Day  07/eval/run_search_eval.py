"""Run semantic search for 10 questions and write eval/search_results.md."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import sys

from app.embed import get_embedder
from app.vectorstore import AapdaMitraVectorStore


EVAL_DIR = Path(__file__).resolve().parent
PROJECT_DIR = EVAL_DIR.parent
DEFAULT_QUESTIONS = EVAL_DIR / "questions.txt"


def load_questions(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Questions file not found: {path}")

    questions: list[str] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("```"):
            continue

        # Supports numbered lists, bullets, and "Question: ..." Markdown.
        line = re.sub(r"^\s*(?:[-*]\s+|\d+\s*[.)]\s*)", "", line)
        match = re.search(r"^\**\s*Question(?:\s*\d+)?\s*:\**\s*(.+)$", line, re.I)
        if match:
            line = match.group(1).strip()
        line = re.sub(r"^\*\*(.*?)\*\*$", r"\1", line).strip()
        if line and not line.startswith("|") and not line.startswith("---"):
            questions.append(line)

    # Preserve order while removing duplicate question lines.
    unique = []
    seen = set()
    for question in questions:
        key = question.casefold()
        if key not in seen:
            seen.add(key)
            unique.append(question)
    return unique[:10]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--questions-file",
        default=str(DEFAULT_QUESTIONS),
        help="Text/Markdown file containing the 10 evaluation questions.",
    )
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--output",
        default=str(EVAL_DIR / "search_results.md"),
    )
    args = parser.parse_args()

    questions_path = Path(args.questions_file).expanduser().resolve()
    questions = load_questions(questions_path)
    if len(questions) != 10:
        raise SystemExit(
            f"Expected 10 questions, but parsed {len(questions)} from {questions_path}.\n"
            "Put one question per line in eval/questions.txt, or pass a file with 10 clear "
            "numbered questions using --questions-file."
        )

    store = AapdaMitraVectorStore()
    if store.count() == 0:
        raise SystemExit(
            "Chroma has no indexed chunks. First run: python -m app.index_documents"
        )

    embedder = get_embedder()
    lines = [
        "# AapdaMitra Semantic Search Results",
        "",
        f"- Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Questions file: `{questions_path}`",
        f"- Chroma collection: `{store.collection_name}`",
        f"- Indexed chunks: {store.count()}",
        f"- Results per question: {args.top_k}",
        "",
        "> These results are generated from the documents currently placed in `documents/`.",
        "",
    ]

    for number, question in enumerate(questions, start=1):
        hits = store.search(question, embedder, top_k=args.top_k)
        lines.extend([f"## Q{number}. {question}", ""])
        if not hits:
            lines.extend(["No matching chunks returned.", ""])
            continue

        for rank, hit in enumerate(hits, start=1):
            snippet = re.sub(r"\s+", " ", hit["text"]).strip()
            if len(snippet) > 500:
                snippet = snippet[:497].rstrip() + "..."
            lines.extend(
                [
                    f"### Hit {rank}",
                    f"- **Title:** {hit['title']}",
                    f"- **Source:** `{hit['source']}`",
                    f"- **Page:** {hit['page']}",
                    f"- **Similarity:** {hit['similarity']:.4f}",
                    f"- **Distance:** {hit['distance']:.4f}",
                    f"- **Text:** {snippet}",
                    "",
                ]
            )

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Search evaluation complete: {output_path}")
    print(f"Questions evaluated: {len(questions)}")
    print(f"Indexed chunks searched: {store.count()}")


if __name__ == "__main__":
    main()
