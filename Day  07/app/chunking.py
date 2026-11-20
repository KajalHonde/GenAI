
"""Load and chunk AapdaMitra HTML documents."""

from pathlib import Path

from bs4 import BeautifulSoup


def load_documents(folder_path):
    documents = []
    folder = Path(folder_path)

    for file_path in folder.glob("*.html"):
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")

        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        else:
            title = file_path.stem

        for element in soup(
            ["script", "style", "nav", "footer", "header"]
        ):
            element.decompose()

        # Keep headings with their related content.
        sections = []
        current_heading = title
        current_text = []

        for element in soup.find_all(
            ["h1", "h2", "h3", "p", "li"]
        ):
            text = element.get_text(" ", strip=True)

            if not text:
                continue

            if element.name in ["h1", "h2", "h3"]:
                if current_text:
                    sections.append({
                        "heading": current_heading,
                        "text": " ".join(current_text)
                    })
                    current_text = []

                current_heading = text
            else:
                current_text.append(text)

        if current_text:
            sections.append({
                "heading": current_heading,
                "text": " ".join(current_text)
            })

        # Fallback if no sections were extracted.
        if not sections:
            text = soup.get_text(" ", strip=True)
            if text:
                sections.append({
                    "heading": title,
                    "text": text
                })

        for section in sections:
            documents.append({
                "text": section["text"],
                "source": file_path.name,
                "title": section["heading"],
                "page": "Not available"
            })

    return documents


def create_chunks(documents, chunk_size=100, overlap=20):
    all_chunks = []

    for document in documents:
        words = document["text"].split()

        start = 0
        chunk_number = 1

        while start < len(words):
            end = start + chunk_size
            chunk_text = " ".join(words[start:end])

            all_chunks.append({
                "text": chunk_text,
                "source": document["source"],
                "title": document["title"],
                "page": document.get("page", "Not available"),
                "chunk_number": chunk_number
            })

            if end >= len(words):
                break

            start += chunk_size - overlap
            chunk_number += 1

    return all_chunks
