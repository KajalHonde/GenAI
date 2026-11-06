"""AapdaMitra record layer: load, validate, search, filter, add, delete, save."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_records.json"
SEVERITIES = ("low", "medium", "high")
REQUIRED = ("title", "severity", "regions", "before", "during", "after", "helpline")


class RecordError(ValueError):
    """Raised when a record is invalid or not found."""


def load_records(path: Path = DATA_FILE) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_records(records: list[dict], path: Path = DATA_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def validate(record: dict) -> dict:
    missing = [k for k in REQUIRED if not record.get(k)]
    if missing:
        raise RecordError(f"Missing fields: {', '.join(missing)}")
    if record["severity"] not in SEVERITIES:
        raise RecordError(f"severity must be one of {SEVERITIES}")
    if not {"name", "number"} <= set(record["helpline"]):
        raise RecordError("helpline needs 'name' and 'number'")
    return record


def next_id(records: Iterable[dict]) -> int:
    return max((r["id"] for r in records), default=0) + 1


def get_by_id(records: list[dict], rec_id: int) -> dict:
    for r in records:
        if r["id"] == rec_id:
            return r
    raise RecordError(f"No record with id {rec_id}")


def filter_by_severity(records: list[dict], level: str) -> list[dict]:
    return [r for r in records if r["severity"] == level.lower()]


def search(records: list[dict], query: str) -> list[dict]:
    """Keyword search ranked by weighted hits (title > tags > regions > text)."""
    words = [w for w in query.lower().split() if w]
    if not words:
        return []
    scored = []
    for r in records:
        score = 0
        for w in words:
            score += 5 * (w in r["title"].lower())
            score += 3 * any(w in t for t in r.get("tags", []))
            score += 2 * (w in r["regions"].lower())
            score += 1 * any(w in r[f].lower() for f in ("before", "during", "after"))
        if score:
            scored.append((score, r))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [r for _, r in scored]


def add_record(records: list[dict], new: dict) -> dict:
    new = validate(dict(new))
    new["id"] = next_id(records)
    new.setdefault("tags", [new["title"].lower()])
    records.append(new)
    return new


def delete_record(records: list[dict], rec_id: int) -> dict:
    rec = get_by_id(records, rec_id)
    records.remove(rec)
    return rec


def summarize(records: list[dict]) -> dict[str, int]:
    counts = {s: 0 for s in SEVERITIES}
    for r in records:
        counts[r["severity"]] += 1
    return counts
