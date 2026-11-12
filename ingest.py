"""Extract and validate candidate action records from downloaded NDMA HTML."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re

from app.models import ActionRecord

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "records.jsonl"

SOURCE_URLS = {
    "ndma_guidelines.html": "https://ndma.gov.in/en/guidelines",
    "flood_dos_donts.html": "https://ndma.gov.in/en/floods-dos-donts",
    "ndma_home.html": "https://ndma.gov.in/en",
}

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            value = " ".join(data.split())
            if value:
                self.parts.append(value)

def classify_hazard(text, filename):
    value = (text + " " + filename).lower()
    if any(word in value for word in ("flood", "floodwater", "inundat")):
        return "flood"
    if any(word in value for word in ("heatwave", "heat wave", "hot weather")):
        return "heatwave"
    if any(word in value for word in ("earthquake", "seismic", "tremor")):
        return "earthquake"
    return "general"

def classify_phase(text):
    value = text.lower()
    if any(word in value for word in ("before", "prepare", "preparedness", "keep ready")):
        return "before"
    if any(word in value for word in ("evacuate", "warning", "alert", "likely")):
        return "likely"
    if any(word in value for word in ("after", "recovery", "return home")):
        return "after"
    if any(word in value for word in ("during", "do not", "don't", "avoid", "stay away")):
        return "during"
    return "unknown"

def extract_records():
    records = []
    next_id = 1

    for path in sorted(RAW_DIR.glob("*.html")):
        try:
            parser = TextExtractor()
            parser.feed(path.read_text(encoding="utf-8", errors="replace"))
            page_text = " ".join(parser.parts)
            candidates = re.split(r"(?<=[.!?])\\s+|(?<=:)\\s+", page_text)

            for candidate in candidates:
                sentence = " ".join(candidate.split()).strip(" •-–:;")
                if not 35 <= len(sentence) <= 450:
                    continue
                lower = sentence.lower()
                if not any(word in lower for word in (
                    "should", "must", "avoid", "do not", "don't", "keep",
                    "move", "stay", "follow", "prepare", "ensure", "never"
                )):
                    continue

                hazard = classify_hazard(sentence, path.name)
                if hazard == "general":
                    continue
                do_or_dont = "dont" if any(
                    word in lower for word in ("do not", "don't", "never", "avoid")
                ) else "do"

                record = ActionRecord(
                    id=next_id,
                    hazard=hazard,
                    phase=classify_phase(sentence),
                    action=sentence,
                    do_or_dont=do_or_dont,
                    who_it_is_for="Residents and families; verify the original page context",
                    what_it_is_for="Candidate guidance extracted from an NDMA page; review before public use",
                    source_url=SOURCE_URLS.get(path.name, "https://ndma.gov.in/en"),
                )
                try:
                    record.validate()
                    records.append(record.to_dict())
                    next_id += 1
                except (TypeError, ValueError) as exc:
                    print(f"[SKIP] Invalid extracted record from {path.name}: {exc}")

        except (OSError, UnicodeError, ValueError) as exc:
            print(f"[ERROR] Could not process {path.name}: {exc}")

    return records

def save_records(records):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    saved = 0
    try:
        with OUTPUT.open("w", encoding="utf-8") as handle:
            for item in records:
                try:
                    validated = ActionRecord.from_dict(item).to_dict()
                    key = validated["action"].casefold()
                    if key in seen:
                        continue
                    seen.add(key)
                    handle.write(json.dumps(validated, ensure_ascii=False) + "\\n")
                    saved += 1
                except (TypeError, ValueError, KeyError) as exc:
                    print(f"[SKIP] Bad record: {exc}")
    except OSError as exc:
        print(f"[ERROR] Could not write {OUTPUT}: {exc}")
        return 0
    return saved

if __name__ == "__main__":
    extracted = extract_records()
    total = save_records(extracted)
    print(f"Saved {total} validated candidate records to {OUTPUT}")
    print("Review every extracted action against its original NDMA page before use.")
