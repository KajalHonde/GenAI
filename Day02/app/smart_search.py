"""TF-IDF and cosine-similarity search for AapdaMitra records."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _record_text(record: dict) -> str:
    fields = (
        "hazard", "phase", "action", "do_or_dont",
        "who_it_is_for", "what_it_is_for",
    )
    return " ".join(str(record.get(field, "")) for field in fields)


def rank_records(query: str, records: list[dict], limit: int = 10) -> list[dict]:
    """Return records ordered by TF-IDF cosine similarity to the query."""
    query = str(query).strip()
    if not query or not records:
        return []

    documents = [_record_text(record) for record in records]
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform(documents + [query])
    except ValueError:
        # Handles a corpus/query containing no usable terms.
        return []

    query_vector = matrix[-1]
    record_matrix = matrix[:-1]
    scores = cosine_similarity(query_vector, record_matrix).flatten()

    ranked = []
    for index, score in enumerate(scores):
        if score > 0:
            item = dict(records[index])
            item["score"] = round(float(score), 4)
            ranked.append(item)

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:limit]
