"""AapdaMitra command-line interface.  Run:  python -m app.cli"""
from __future__ import annotations

import textwrap

from app import records as rec

ICON = {"low": "🟢", "medium": "🟠", "high": "🔴"}


def wrap(label: str, text: str) -> str:
    return textwrap.fill(text, width=76, initial_indent=f"  {label:<8}",
                         subsequent_indent=" " * 10)


def show_brief(r: dict) -> None:
    print(f"  [{r['id']:>2}] {ICON[r['severity']]} {r['title']}  ({r['severity']})")


def show_full(r: dict) -> None:
    print(f"\n{ICON[r['severity']]} {r['title'].upper()}  | severity: {r['severity']}")
    print(wrap("Where:", r["regions"]))
    print(wrap("Before:", r["before"]))
    print(wrap("During:", r["during"]))
    print(wrap("After:", r["after"]))
    h = r["helpline"]
    print(f"  Call:    {h['number']} ({h['name']})\n")


def ask_int(prompt: str) -> int | None:
    raw = input(prompt).strip()
    return int(raw) if raw.isdigit() else None


def do_list(data):
    for r in data:
        show_brief(r)
    print("  Totals:", rec.summarize(data))


def do_view(data):
    rid = ask_int("Record id: ")
    if rid is None:
        print("Please enter a number.")
        return
    show_full(rec.get_by_id(data, rid))


def do_search(data):
    hits = rec.search(data, input("Search words: "))
    if not hits:
        print("  Nothing found.")
    for r in hits[:5]:
        show_brief(r)


def do_filter(data):
    level = input(f"Severity {rec.SEVERITIES}: ").strip().lower()
    if level not in rec.SEVERITIES:
        print("Unknown severity.")
        return
    for r in rec.filter_by_severity(data, level):
        show_brief(r)


def do_add(data):
    print("Add a new record (leave blank to cancel).")
    title = input("Title: ").strip()
    if not title:
        return
    new = {
        "title": title,
        "severity": input("Severity (low/medium/high): ").strip().lower(),
        "regions": input("Regions at risk: ").strip(),
        "before": input("Before: ").strip(),
        "during": input("During: ").strip(),
        "after": input("After: ").strip(),
        "helpline": {"name": input("Helpline name: ").strip(),
                     "number": input("Helpline number: ").strip()},
    }
    added = rec.add_record(data, new)
    rec.save_records(data)
    print(f"  Saved as id {added['id']}.")


def do_delete(data):
    rid = ask_int("Id to delete: ")
    if rid is None:
        print("Please enter a number.")
        return
    gone = rec.delete_record(data, rid)
    rec.save_records(data)
    print(f"  Deleted '{gone['title']}'.")


MENU = {
    "1": ("List all records", do_list),
    "2": ("View one record", do_view),
    "3": ("Search", do_search),
    "4": ("Filter by severity", do_filter),
    "5": ("Add record", do_add),
    "6": ("Delete record", do_delete),
}


def main() -> None:
    data = rec.load_records()
    print(f"AapdaMitra loaded {len(data)} records. Emergency: dial 112.")
    while True:
        print("\n--- Menu ---")
        for k, (label, _) in MENU.items():
            print(f" {k}. {label}")
        print(" 0. Exit")
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Stay safe!")
            return
        entry = MENU.get(choice)
        if not entry:
            print("Invalid choice.")
            continue
        try:
            entry[1](data)
        except rec.RecordError as err:
            print(f"  Error: {err}")


if __name__ == "__main__":
    main()
