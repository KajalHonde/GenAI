# AapdaMitra 

AapdaMitra tells families what to do **before, during and after** a flood, heatwave or earthquake, using NDMA's official do's and don'ts and guidelines.

> In a real emergency call **112**. For a heat-related illness call **108**.

## Project card

| | |
|---|---|
| **Product** | AapdaMitra tells families what to do **before, during and after** a flood, heatwave or earthquake, using NDMA's official do's and don'ts and guidelines. |
| **User** | A gram panchayat member in a village on the Godavari bank near Kopargaon, who has to prepare families for the monsoon floods and the April-May heatwave. |
| **Problem** | Safety advice is scattered across long PDFs and web pages, mostly in English. In an emergency a village leader needs one short, correct instruction, fast. |
| **Data source** | NDMA HTML pages and PDF guidelines/advisories: <https://ndma.gov.in/en/guidelines> and <https://ndma.gov.in/en/floods-dos-donts> |

## Progress by day

| Day | Folder | What it adds |
|---|---|---|
| 1 | `day01/` | Project card and greeting; a while-loop menu with a simple heat check |
| 2 | `day02/` | 20 NDMA action records in JSON; a data module (load, search, count, get by id); a command-line menu |
| 3 | `day03/` | Filter by hazard, phase and do/don't (menu option 5); tests |

Each day folder is a self-contained snapshot of the project on that day.

## Requirements

- Python 3.9 or newer.
- Days 1 and 2 use only the Python standard library.
- Day 3 tests need `pytest` (listed in `day03/requirements.txt`).

## Folder structure

```
AapdaMitra/
├── README.md
├── .gitignore
├── requirements.txt
├── day01/
│   ├── day01_intro.py
│   └── day01_menu.py
├── day02/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── records.py
│   │   └── cli.py
│   └── data/
│       └── sample_records.json
└── day03/
    ├── app/
    │   ├── __init__.py
    │   ├── records.py
    │   └── cli.py
    ├── data/
    │   └── sample_records.json
    ├── tests/
    │   ├── __init__.py
    │   └── test_records.py
    └── requirements.txt
```

## Day 1 - Intro and menu

Run from inside `day01/`:

```
python day01_intro.py
python day01_menu.py
```

- `day01_intro.py` prints the project card, asks for the user's name and village, and greets them.
- `day01_menu.py` is a while-loop menu: **1** About, **2** Sample questions, **3** Heat check, **0** Exit.
- The heat check is a simple if/elif demo (37, 40 and 45 °C). It is **not** IMD's official heatwave criteria.

## Day 2 - Data and command-line app

Run from inside `day02/`:

```
python -m app.cli
```

Menu: **1** Show all, **2** Search, **3** Count by hazard, **4** Open by id, **0** Exit.

### Record format

`data/sample_records.json` holds 20 records (7 flood, 7 heatwave, 6 earthquake). Each record has:

| Field | Meaning | Example |
|---|---|---|
| `id` | Unique number | `7` |
| `hazard` | `flood`, `heatwave` or `earthquake` | `flood` |
| `phase` | When to act (before, likely, evacuate, during, first aid, during indoors, during outdoors, trapped under debris) | `evacuate` |
| `action` | The instruction in plain words | `Do not walk or drive through flowing flood water.` |
| `do_or_dont` | `do` or `dont` | `dont` |
| `who_it_is_for` | `everyone`, `family` or `farmer` | `everyone` |
| `source_url` | NDMA page the record comes from | `https://ndma.gov.in/en/floods-dos-donts` |

### Functions in `app/records.py`

| Function | What it does |
|---|---|
| `load_records(path)` | Reads all records from the JSON file |
| `search(records, keyword)` | Records whose hazard, phase, action or audience contains the keyword |
| `count_by(records, field)` | Number of records per value of a field, e.g. per hazard |
| `get_by_id(records, rec_id)` | One record by id, or `None` |

## Day 3 - Filter and tests

Run from inside `day03/`:

```
python -m app.cli
pip install -r requirements.txt
pytest
```

- Adds `filter_records(records, hazard, phase, do_or_dont)` to `app/records.py`. Blank filters are ignored, and all given filters must match.
- Adds menu option **5. Filter** to the CLI. Example: hazard `flood`, phase blank, `dont` gives record 7.
- `tests/test_records.py` checks the record count (20), the counts per hazard (7 / 7 / 6), search, get by id, and filtering.

## Records by hazard

| Hazard | Records | NDMA page |
|---|---|---|
| Flood | 7 (before / likely / evacuate) | floods-dos-donts |
| Heatwave | 7 (before / during / first aid, including sunstroke tips) | Heat-Wave Dos-Donts |
| Earthquake | 6 (before / during indoors / during outdoors / trapped under debris) | guidelines |

## Notes

- Run `python -m app.cli` from inside `day02/` or `day03/`, not from inside `app/`, or the imports will fail.
- The advice comes from NDMA pages. Check the `source_url` of a record for the full official text.
