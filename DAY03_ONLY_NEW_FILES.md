# AapdaMitra 

This is an incremental update. It contains only the new Day 03 modules and
the updated requirements.txt. It does NOT include or replace Day 01/Day 02
files such as README.md, app/records.py, app/cli.py, or existing datasets.

## New files
- app/fetch.py
- app/ingest.py
- app/models.py
- data/raw/README.txt

## Updated existing file
- requirements.txt (adds the `requests` dependency)

## Run from your existing repository root
```bash
pip install -r requirements.txt
python -m app.fetch
python -m app.ingest
```

The fetch script attempts to download three NDMA pages. The ingest script
extracts candidate action text, validates the required fields, and creates
`data/records.jsonl`. That JSONL file is generated when you run ingestion;
it is not bundled here, so no Day 02 data is duplicated.

Official sources:
- https://ndma.gov.in/en/guidelines
- https://ndma.gov.in/en/floods-dos-donts
- https://ndma.gov.in/en

Review extracted candidate text in its original context before using it as
public safety advice. Follow current NDMA and local authority instructions.
