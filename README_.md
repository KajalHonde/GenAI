# AapdaMitra (आपदा मित्र) - Day 2

Day 2 adds the **data layer** and a **command-line app**: 20 NDMA action records that you can show, search, count and open by id.

## Project card

| | |
|---|---|
| **Product** | AapdaMitra tells families what to do **before, during and after** a flood, heatwave or earthquake, using NDMA's official do's and don'ts and guidelines. |
| **User** | A gram panchayat member in a village on the Godavari bank near Kopargaon, who has to prepare families for the monsoon floods and the April-May heatwave. |
| **Problem** | Safety advice is scattered across long PDFs and web pages, mostly in English. In an emergency a village leader needs one short, correct instruction, fast. |
| **Data source** | NDMA HTML pages and PDF guidelines/advisories: <https://ndma.gov.in/en/guidelines> and <https://ndma.gov.in/en/floods-dos-donts> |

## What Day 2 adds

- A JSON file with **20 action records** (7 flood, 7 heatwave, 6 earthquake).
- A data module, `records.py`, with four functions: `load_records`, `search`, `count_by`, `get_by_id`.
- A menu-driven CLI, `cli.py`, that uses those functions.

## Record format

Each record in `data/sample_records.json` has these fields:

| Field | Meaning | Example |
|---|---|---|
| `id` | Unique number | `7` |
| `hazard` | `flood`, `heatwave` or `earthquake` | `flood` |
| `phase` | When to act (before, likely, evacuate, during, first aid, during indoors, during outdoors, trapped under debris) | `evacuate` |
| `action` | The instruction in plain words | `Do not walk or drive through flowing flood water.` |
| `do_or_dont` | `do` or `dont` | `dont` |
| `who_it_is_for` | `everyone`, `family` or `farmer` | `everyone` |
| `source_url` | NDMA page the record comes from | `https://ndma.gov.in/en/floods-dos-donts` |

## Records by hazard

| Hazard | Records | NDMA page |
|---|---|---|
| Flood | 7 (before / likely / evacuate) | floods-dos-donts |
| Heatwave | 7 (before / during / first aid) | Heat-Wave Dos-Donts |
| Earthquake | 6 (before / during indoors / outdoors / trapped under debris) | guidelines |

## How to run

Run from inside the `day02` folder (Python 3.9+, no extra packages):

```
python -m app.cli
```

Menu:

```
1. Show all   2. Search   3. Count by hazard   4. Open by id   0. Exit
```

- **Show all** lists every record in one line each.
- **Search** finds records whose hazard, phase, action or audience contains your keyword (for example `ORS` or `flood`).
- **Count by hazard** shows how many records each hazard has.
- **Open by id** shows one record in full, with its source link.

## Files

```
day02/
├── app/
│   ├── __init__.py
│   ├── records.py      # load_records, search, count_by, get_by_id
│   └── cli.py          # command-line menu
└── data/
    └── sample_records.json   # 20 action records
```

## Notes

- Always run `python -m app.cli` from `day02`, not from inside `app/`, or the imports will fail.
- The sunstroke first-aid tips are included in the heatwave records (ids 12 and 13).
- In a real emergency call **112**. For a heat-related illness call **108**.
