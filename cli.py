"""AapdaMitra command-line app.  Run from the repo root:  python -m app.cli"""
import textwrap

from app.records import count_by, get_by_id, load_records, search


def show(r: dict) -> None:
    tag = "DO   " if r["do_or_dont"] == "do" else "DON'T"
    print(f"[{r['id']:>2}] {r['hazard']:<10} {r['phase']:<20} {tag}")


def show_full(r: dict) -> None:
    print(f"\n{r['hazard'].upper()} - {r['phase']}  ({r['do_or_dont'].upper()}, for: {r['who_it_is_for']})")
    print(textwrap.fill(r["action"], width=76, initial_indent="  ", subsequent_indent="  "))
    print(f"  Source: {r['source_url']}")


def main() -> None:
    records = load_records()
    print(f"AapdaMitra: {len(records)} NDMA records loaded.")
    while True:
        print("\n1. Show all   2. Search   3. Count by hazard   4. Open by id   0. Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            for r in records:
                show(r)
        elif choice == "2":
            hits = search(records, input("Keyword: "))
            print(f"{len(hits)} match(es)")
            for r in hits:
                show_full(r)
        elif choice == "3":
            for hazard, n in count_by(records, "hazard").items():
                print(f"  {hazard:<10} {n}")
        elif choice == "4":
            raw = input("Record id: ").strip()
            r = get_by_id(records, int(raw)) if raw.isdigit() else None
            show_full(r) if r else print("No record with that id.")
        elif choice == "0":
            print("Stay safe!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
