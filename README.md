# AapdaMitra

> A "disaster friend" for everyday Indians: quick, offline-friendly guidance on what to do **before, during and after** a disaster, plus the right helpline to call.

## Project Card

| Field | Details |
|---|---|
| **Name** | AapdaMitra |
| **Author** | Kajal Honde |
| **Problem** | During floods, lightning, heatwaves or fires, people lose precious minutes searching for reliable steps and helpline numbers. Advice is scattered, often in English only, and often unavailable offline. |
| **Users** | Villagers, students, families and local volunteers in flood/drought/heat-prone regions (e.g. the Godavari basin, Maharashtra). |
| **Core idea** | A structured knowledge base of disaster records, searchable from a CLI today, and used as grounding data for a GenAI (RAG) assistant later. |
| **GenAI plan** | Retrieve the most relevant record, then let an LLM explain it in simple Marathi/Hindi/English, grounded only in the stored record to avoid made-up safety advice. |
| **Stack** | Python 3, JSON storage, argparse-free CLI (stdlib only) |

## Roadmap

- [x] **D1**: Project card, intro script, text menu
- [x] **D2**: JSON records (18) + records module + CLI
- [ ] **D3**: Search ranking and tests
- [ ] **D4+**: LLM-powered answers grounded in records

## Run

```bash
python day01_intro.py
python day01_menu.py
python -m app.cli
```

## Structure

```
GenAI/
├── README.md
├── day01_intro.py
├── day01_menu.py
├── data/sample_records.json
└── app/
    ├── records.py   # load / validate / search / add / delete
    └── cli.py       # interactive menu
```

## Safety note

AapdaMitra is a learning project. In a real emergency call **112** first.
