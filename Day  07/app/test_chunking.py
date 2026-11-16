
from pathlib import Path

from app.chunking import load_documents, create_chunks


BASE_DIR = Path(__file__).resolve().parents[1]

DOCUMENTS_PATH = BASE_DIR / "documents"


print("\nLoading documents...\n")

documents = load_documents(DOCUMENTS_PATH)

print("Total documents:", len(documents))

for document in documents:
    print("\nSource:", document["source"])
    print("Title:", document["title"])


print("\nCreating chunks...\n")

chunks = create_chunks(documents)

print("Total chunks:", len(chunks))


for chunk in chunks[:5]:

    print("\n-------------------------")

    print("Source:", chunk["source"])
    print("Title:", chunk["title"])
    print("Page:", chunk["page"])
    print("Chunk:", chunk["chunk_number"])
    print("Text:", chunk["text"][:150])


print("\nChunking test completed!")
