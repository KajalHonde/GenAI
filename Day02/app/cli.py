"""Simple command-line menu for AapdaMitra Day 02."""

from app.records import load_records, search_records, count_by, get_by_id


def show_records(items):
    if not items:
        print("No records found.")
        return
    for item in items:
        print(
            f"\\nID: {item['id']} | Hazard: {item['hazard']} | "
            f"Phase: {item['phase']} | {item['do_or_dont'].upper()}"
        )
        print(f"Action: {item['action']}")
        print(f"For: {item['who_it_is_for']}")
        print(f"Purpose: {item['what_it_is_for']}")
        print(f"Source: {item['source_url']}")


def main():
    while True:
        print("\\n========== AAPDAMITRA DAY 02 ==========")
        print("1. Show all action records")
        print("2. Search records by keyword")
        print("3. Count records by hazard")
        print("4. Find a record by ID")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_records(load_records())
        elif choice == "2":
            keyword = input("Enter a keyword (e.g. water, river, safe): ")
            show_records(search_records(keyword))
        elif choice == "3":
            print("Counts by hazard:")
            print(count_by("hazard"))
        elif choice == "4":
            record_id = input("Enter record ID (1-20): ")
            record = get_by_id(record_id)
            show_records([record] if record else [])
        elif choice == "0":
            print("Thank you for using AapdaMitra. Stay safe!")
            break
        else:
            print("Invalid choice. Please select 0, 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()
