"""AapdaMitra data layer: load, search, count and look up NDMA records."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_records.json"


def load_records(path: Path | str = DATA_FILE) -> list[dict]:
    """Read all records from the JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def search(records: list[dict], keyword: str) -> list[dict]:
    """Return records whose title, action, hazard or keywords contain `keyword`."""
    kw = keyword.strip().lower()
    if not kw:
        return []
    hits = []
    for r in records:
        text = " ".join([r["title"], r["action"], r["hazard"], r["phase"], *r["keywords"]]).lower()
        if kw in text:
            hits.append(r)
    return hits


def count_by(records: list[dict], field: str) -> dict[str, int]:
    """Count records per value of `field`, e.g. count_by(records, 'hazard')."""
    return dict(Counter(r[field] for r in records))


def get_by_id(records: list[dict], rec_id: int) -> dict | None:
    """Return the record with this id, or None if it does not exist."""
    for r in records:
        if r["id"] == rec_id:
            return r
    return None
