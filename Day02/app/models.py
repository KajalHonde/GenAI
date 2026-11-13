"""Validated action-record model for AapdaMitra."""
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

VALID_HAZARDS = {"heatwave", "flood", "earthquake", "general"}
VALID_PHASES = {"before", "likely", "during", "after", "unknown"}
VALID_ACTION_TYPES = {"do", "dont", "info"}

@dataclass
class ActionRecord:
    id: int
    hazard: str
    phase: str
    action: str
    do_or_dont: str
    who_it_is_for: str
    what_it_is_for: str
    source_url: str

    def validate(self):
        if type(self.id) != int or self.id < 1:
            raise ValueError("id must be a positive integer")
        if self.hazard not in VALID_HAZARDS:
            raise ValueError(f"Invalid hazard: {self.hazard}")
        if self.phase not in VALID_PHASES:
            raise ValueError(f"Invalid phase: {self.phase}")
        if self.do_or_dont not in VALID_ACTION_TYPES:
            raise ValueError(f"Invalid do_or_dont: {self.do_or_dont}")
        for field in ("action", "who_it_is_for", "what_it_is_for", "source_url"):
            if not str(getattr(self, field)).strip():
                raise ValueError(f"{field} cannot be empty")
        parsed = urlparse(self.source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be a valid HTTP(S) URL")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        record = cls(**data)
        record.validate()
        return record