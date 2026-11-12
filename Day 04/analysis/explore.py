"""Print three basic facts about AapdaMitra records using pandas."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RECORDS_FILE = ROOT / "data" / "records.jsonl"


def load_data() -> pd.DataFrame:
    if not RECORDS_FILE.exists():
        from app.records import load_records
        records = load_records()
    else:
        records = []
        with RECORDS_FILE.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return pd.DataFrame(records)


def main():
    df = load_data()
    if df.empty:
        print("No records found. Run Day 03 ingestion first.")
        return

    print("========== AAPDAMITRA: 3 DATA FACTS ==========")

    # Fact 1
    print(f"1. Total action records: {len(df)}")

    # Fact 2
    hazard_counts = df["hazard"].value_counts()
    print("2. Records by hazard:")
    print(hazard_counts.to_string())

    # Fact 3
    action_counts = df["do_or_dont"].value_counts()
    print("3. Records by action type (do/dont/info):")
    print(action_counts.to_string())


if __name__ == "__main__":
    main()
