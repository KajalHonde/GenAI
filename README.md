# AapdaMitra (आपदा मित्र)

NDMA do's and don'ts (flood, heatwave, earthquake) for a gram panchayat member near Kopargaon.
In a real emergency call **112**.

| Day | Folder | What it adds | Run (from inside the day folder) |
|---|---|---|---|
| 1 | `day01/` | Project card + greeting, while-loop menu with heat check | `python day01_intro.py` / `python day01_menu.py` |
| 2 | `day02/` | 20-record JSON data + `records.py` (load/search/count/get) + CLI | `python -m app.cli` |
| 3 | `day03/` | `filter_records` (hazard/phase/do-dont), menu option 5, pytest tests | `python -m app.cli` / `pytest` |

Each day folder is a self-contained snapshot, so you can commit one per day.
