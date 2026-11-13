
"""Clean and validate candidate action records from downloaded NDMA HTML."""

from html.parser import HTMLParser
from pathlib import Path
import json
import re

from app.models import ActionRecord


# Project paths
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "records.json"


# Actual downloaded filenames and their original NDMA URLs
SOURCE_URLS = {
    "flood_dos_donts.html":
        "https://ndma.gov.in/en/floods-dos-donts",

    "ndma_guidelines.html":
        "https://ndma.gov.in/en/guidelines",

    "ndma_home.html":
        "https://ndma.gov.in/en",
}


# Extract readable text from downloaded HTML
class TextExtractor(HTMLParser):

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):

        if tag in ("script", "style", "noscript", "svg"):
            self.skip_depth += 1
            return

        if not self.skip_depth and tag in (
            "p", "li", "br", "div", "h1",
            "h2", "h3", "h4", "tr"
        ):
            self.parts.append("\n")

    def handle_endtag(self, tag):

        if tag in ("script", "style", "noscript", "svg"):
            if self.skip_depth:
                self.skip_depth -= 1
            return

        if not self.skip_depth and tag in (
            "p", "li", "div", "h1",
            "h2", "h3", "h4", "tr"
        ):
            self.parts.append("\n")

    def handle_data(self, data):

        if not self.skip_depth:
            value = " ".join(data.split())

            if value:
                self.parts.append(value)


# Identify disaster type
def classify_hazard(text, filename):

    value = (text + " " + filename).lower()

    if any(word in value for word in (
        "flood", "floodwater", "inundation"
    )):
        return "flood"

    if any(word in value for word in (
        "heatwave", "heat wave", "hot weather"
    )):
        return "heatwave"

    if any(word in value for word in (
        "earthquake", "seismic", "tremor"
    )):
        return "earthquake"

    return "general"


def classify_phase(text):
    value = text.lower().strip()

    # Preparation and prevention
    if any(word in value for word in (
        "prepare",
        "preparedness",
        "building in flood prone areas",
        "install check valves",
        "contact community officials",
        "seal the walls",
        "keep ready"
    )):
        return "before"

    # Warning or possible disaster
    if any(word in value for word in (
        "warning",
        "alert",
        "likely",
        "forecast",
        "possibility"
    )):
        return "likely"

    # Recovery
    if any(word in value for word in (
        "after",
        "recovery",
        "return home"
    )):
        return "after"

    # Active emergency
    if any(word in value for word in (
        "move immediately",
        "evacuate",
        "floodwaters",
        "flood water",
        "moving water",
        "do not wait",
        "do not touch",
        "do not walk",
        "do not drive"
    )):
        return "during"

    return "unknown"
# Correctly classify DO and DON'T instructions
def classify_action_type(text):

    value = text.lower().strip()

    negative_starts = (
        "do not ",
        "don't ",
        "never ",
        "avoid ",
        "must not ",
        "should not ",
        "shouldn't ",
        "cannot ",
        "can not "
    )

    if value.startswith(negative_starts):
        return "dont"

    return "do"


# Identify the likely audience from the instruction
def identify_audience(text, hazard):

    value = text.lower()

    if "child" in value or "children" in value:
        return "Children and their caregivers"

    if any(word in value for word in (
        "car", "drive", "vehicle", "road"
    )):
        return "Drivers and vehicle occupants"

    if any(word in value for word in (
        "basement", "home", "house", "walls"
    )):
        return "Residents and homeowners"

    if hazard == "flood":
        return "People in flood-prone or flood-affected areas"

    if hazard == "earthquake":
        return "People in earthquake-affected areas"

    if hazard == "heatwave":
        return "People exposed to extreme heat"

    return "People to whom this NDMA guidance applies"


# Remove webpage navigation and irrelevant content
def is_irrelevant(text):

    value = text.lower()

    unwanted_phrases = (
        "footer",
        "terms of use",
        "website policy",
        "website content managed",
        "website last updated",
        "sitemap",
        "feedback",
        "view all",
        "download",
        "copyright",
        "archives",
        "chevron_right",
        "national disaster management authority",
        "help",
        "tender",
        "privacy policy",
        "skip to main content"
    )

    return any(
        phrase in value for phrase in unwanted_phrases
    )


# Reject incomplete instructions
def is_incomplete(text):
    value = text.lower().strip()
    words = value.split()

    # Reject short headings and fragments
    if len(words) < 7:
        return True

    incomplete_endings = (
        "you should",
        "you must",
        "you can",
        "you may",
        "if you must",
        "such as",
        "including",
        "because",
        "and",
        "or",
        "to",
        "of",
        "with",
        "for"
    )

    if value.endswith(incomplete_endings):
        return True

    # Reject common webpage headings
    heading_phrases = (
        "early warning",
        "preparedness",
        "heat wave",
        "dos and donts",
        "do's and don'ts",
        "guidelines"
    )

    if any(phrase in value for phrase in heading_phrases):
        return True

    return False


# Check for a genuine action candidate
def is_action_candidate(text):

    value = text.lower()

    action_words = (
        "should",
        "must",
        "avoid",
        "do not",
        "don't",
        "keep",
        "move",
        "stay",
        "follow",
        "prepare",
        "ensure",
        "never",
        "use",
        "carry",
        "switch off",
        "contact",
        "evacuate",
        "drink",
        "remain",
        "protect",
        "cover",
        "repair",
        "seal",
        "check"
    )

    return any(
        word in value for word in action_words
    )


# Extract records from actual downloaded HTML files
def extract_records():

    records = []
    next_id = 1

    if not RAW_DIR.exists():
        print("[ERROR] data/raw folder not found.")
        return records

    html_files = sorted(RAW_DIR.glob("*.html"))

    if not html_files:
        print("[ERROR] No downloaded HTML files found.")
        return records

    for path in html_files:

        try:
            print(f"\nReading: {path.name}")

            source_url = SOURCE_URLS.get(path.name)

            if not source_url:
                print("[SKIP] Source URL not mapped.")
                continue

            html = path.read_text(
                encoding="utf-8",
                errors="replace"
            )

            parser = TextExtractor()
            parser.feed(html)
            parser.close()

            page_text = "".join(parser.parts)

            page_text = re.sub(
                r"[ \t]+",
                " ",
                page_text
            )

            print("Extracted text length:", len(page_text))

            if len(page_text) < 100:
                print("[WARNING] Insufficient webpage text.")
                continue

            # Split using sentence endings and HTML block boundaries
            candidates = re.split(
                r"(?<=[.!?])\s+|\n+",
                page_text
            )

            print("Candidates found:", len(candidates))

            for candidate in candidates:

                try:
                    sentence = " ".join(candidate.split())

                    sentence = sentence.strip(
                        " •-–:;×✓‹›"
                    )

                    # Basic quality checks
                    if not 30 <= len(sentence) <= 450:
                        continue

                    if is_irrelevant(sentence):
                        continue

                    if is_incomplete(sentence):
                        continue

                    if not is_action_candidate(sentence):
                        continue

                    hazard = classify_hazard(
                        sentence,
                        path.name
                    )

                    if hazard == "general":
                        continue

                    record = ActionRecord(
                        id=next_id,
                        hazard=hazard,
                        phase=classify_phase(sentence),
                        action=sentence,
                        do_or_dont=classify_action_type(sentence),
                        who_it_is_for=identify_audience(
                            sentence,
                            hazard
                        ),
                        what_it_is_for=(
                            "Candidate disaster safety guidance "
                            "extracted from an NDMA webpage; "
                            "verify original context"
                        ),
                        source_url=source_url
                    )

                    record.validate()

                    records.append(record.to_dict())
                    next_id += 1

                except (TypeError, ValueError, KeyError) as error:
                    print("[SKIP] Invalid candidate:", error)

        except (OSError, UnicodeError, ValueError) as error:
            print(f"[ERROR] Could not process {path.name}: {error}")

    return records


# Remove duplicates and save proper JSON
def save_records(records):

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    unique_records = []
    seen = set()

    for item in records:

        try:
            validated = ActionRecord.from_dict(item).to_dict()

            key = (
                validated["hazard"],
                validated["action"].casefold()
            )

            if key in seen:
                continue

            seen.add(key)
            unique_records.append(validated)

        except (TypeError, ValueError, KeyError) as error:
            print("[SKIP] Invalid record:", error)

    try:
        with OUTPUT.open("w", encoding="utf-8") as file:

            json.dump(
                unique_records,
                file,
                indent=2,
                ensure_ascii=False
            )

        print("\nRecords saved:", len(unique_records))
        print("Output:", OUTPUT)

    except OSError as error:
        print("[ERROR] Could not save records:", error)
        return 0

    return len(unique_records)


# Main execution
if __name__ == "__main__":

    print("Starting NDMA data ingestion...")

    extracted = extract_records()

    total = save_records(extracted)

    print("\n========== INGESTION SUMMARY ==========")
    print("Total valid records:", total)

    if total >= 5:
        print("SUCCESS: Minimum 5 records generated.")
    else:
        print("WARNING: Fewer than 5 records generated.")
        print("Review HTML content and extraction rules.")

    print("=======================================")
