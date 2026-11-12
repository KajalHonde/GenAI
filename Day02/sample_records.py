"""Demonstration of AapdaMitra action-record functions."""

from app.records import load_records, search_records, count_by, get_by_id


def print_record(record):
    print(
        f"ID {record['id']} | {record['hazard']} | {record['phase']} | "
        f"{record['do_or_dont'].upper()} | {record['action']}"
    )


if __name__ == "__main__":
    print("=== ALL ACTION RECORDS ===")
    for item in load_records():
        print_record(item)

    print("\\n=== SEARCH: river ===")
    for item in search_records("river"):
        print_record(item)

    print("\\n=== COUNT BY HAZARD ===")
    print(count_by("hazard"))

    print("\\n=== GET RECORD BY ID: 8 ===")
    item = get_by_id(8)
    if item:
        print_record(item)
    else:
        print("Record not found.")
