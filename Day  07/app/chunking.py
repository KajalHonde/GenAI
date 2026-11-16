
from pathlib import Path
from bs4 import BeautifulSoup


def load_documents(folder_path):

    documents = []

    folder = Path(folder_path)

    for file_path in folder.glob("*.html"):

        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Get document title
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        else:
            title = file_path.stem

        # Remove unnecessary HTML elements
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()

        # Extract text
        text = soup.get_text(separator=" ", strip=True)

        # Store document details
        documents.append({
            "text": text,
            "source": file_path.name,
            "title": title
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
                "page": "Not available",
                "chunk_number": chunk_number
            })

            start += chunk_size - overlap
            chunk_number += 1

    return all_chunks
