
"""Read documents and split them into searchable chunks."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".docx",
    ".html",
}


@dataclass
class DocumentChunk:
    id: str
    text: str
    source: str
    page: int
    title: str


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_document(path: Path):
    suffix = path.suffix.lower()
    fallback_title = path.stem.replace("_", " ").title()

    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((page_number, text, fallback_title))

        return pages

    if suffix == ".docx":
        from docx import Document

        document = Document(str(path))
        text = "\n".join(p.text for p in document.paragraphs)
        text = clean_text(text)

        return [(1, text, fallback_title)] if text else []

    if suffix == ".html":
        from bs4 import BeautifulSoup

        raw_html = path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        soup = BeautifulSoup(raw_html, "html.parser")

        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript"
        ]):
            element.decompose()

        title = (
            soup.title.get_text(" ", strip=True)
            if soup.title
            else fallback_title
        )

        text = clean_text(
            soup.get_text(separator=" ", strip=True)
        )

        return [(1, text, title)] if text else []

    text = path.read_text(
        encoding="utf-8",
        errors="replace"
    )

    return [(1, clean_text(text), fallback_title)]


def split_into_chunks(
    text: str,
    chunk_size: int = 180,
    chunk_overlap: int = 35
):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size"
        )

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        if end == len(words):
            break

        start = end - chunk_overlap

    return chunks


def load_and_chunk_documents(
    documents_dir: str | Path,
    chunk_size: int = 180,
    chunk_overlap: int = 35
):
    documents_path = Path(documents_dir)

    if not documents_path.exists():
        raise FileNotFoundError(
            f"Documents folder not found: {documents_path}"
        )

    all_chunks = []

    files = sorted(
        path for path in documents_path.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    for path in files:
        try:
            pages = read_document(path)

            for page_number, text, title in pages:
                if not text.strip():
                    continue

                pieces = split_into_chunks(
                    text,
                    chunk_size,
                    chunk_overlap
                )

                for chunk_number, piece in enumerate(pieces):
                    chunk_id = sha256(
                        (
                            f"{path.name}|{page_number}|"
                            f"{chunk_number}|{piece}"
                        ).encode("utf-8")
                    ).hexdigest()

                    all_chunks.append(
                        DocumentChunk(
                            id=chunk_id,
                            text=piece,
                            source=path.name,
                            page=page_number,
                            title=title
                        )
                    )

        except Exception as error:
            print(
                f"Skipping {path.name}: "
                f"{type(error).__name__}: {error}"
            )

    return all_chunks
