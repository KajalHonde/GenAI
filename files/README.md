# AapdaMitra (आपदा मित्र)

## Project card

| | |
|---|---|
| **Product** | AapdaMitra tells families what to do **before, during and after** a flood, heatwave or earthquake, using NDMA's official do's and don'ts and guidelines. |
| **User** | A gram panchayat member in a village on the Godavari bank near Kopargaon, who has to prepare families for the monsoon floods and the April-May heatwave. |
| **Problem** | Safety advice is scattered across long PDFs and web pages, mostly in English. In an emergency a village leader needs one short, correct instruction, fast. |
| **Data source** | NDMA (National Disaster Management Authority) HTML pages and PDF guidelines/advisories: <https://ndma.gov.in/en/guidelines> and <https://ndma.gov.in/en/floods-dos-donts> |

## How to run

```
python day01_intro.py
python day01_menu.py
python -m app.cli
```

## Files

- `day01_intro.py` - prints the project card and greets the user
- `day01_menu.py` - small menu: about, sample questions, heat rule check
- `data/sample_records.json` - 18 records (one NDMA do/don't each)
- `app/records.py` - load_records, search, count_by, get_by_id
- `app/cli.py` - command-line menu using records.py

In a real emergency call **112**.
