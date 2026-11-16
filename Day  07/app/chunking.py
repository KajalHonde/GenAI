
from pathlib import Path
from bs4 import BeautifulSoup


def extract_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # Extract document title
    title_tag = soup.find("h1") or soup.find("title")

    if title_tag:
        title = title_tag.get_text(strip=True)
    else:
        title = file_path.stem

    # Remove unnecessary HTML elements
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    # Extract useful text
    content = soup.find("main") or soup.body or soup
    text = content.get_text(separator=" ", strip=True)

    return text, title


def create_chunks(text, chunk_size=100, overlap=20):
    words = text.split()

    if overlap >= chunk_size or overlap < 0:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def load_documents(documents_dir=None):
    if documents_dir is None:
        documents_dir = (
            Path(__file__).resolve().parent.parent / "documents"
        )

    documents_dir = Path(documents_dir)

    all_chunks = []

    for file_path in sorted(documents_dir.glob("*.html")):

        text, title = extract_text(file_path)

        chunks = create_chunks(text)

        for index, chunk in enumerate(chunks):

            record = {
                "id": f"{file_path.stem}_{index}",
                "text": chunk,
                "metadata": {
                    "source": file_path.name,
                    "page": 1,
                    "title": title
                }
            }

            all_chunks.append(record)

    return all_chunks


if __name__ == "__main__":
    documents = load_documents()

    print("Total chunks:", len(documents))

    for document in documents[:3]:
        print("\nText:", document["text"])
        print("Metadata:", document["metadata"])
