"""Day 1 - AapdaMitra text menu (dictionary-driven, no if/elif chain)."""

HELPLINES = {
    "112": "National emergency number",
    "108": "Ambulance",
    "101": "Fire brigade",
    "100": "Police",
    "1078": "NDMA disaster control room",
    "1091": "Women helpline",
}

TIPS = {
    "flood": "Move to higher ground, switch off power, never walk through moving water.",
    "lightning": "Avoid open fields and tall trees; shelter in a building, not under a tree.",
    "heatwave": "Drink water often, avoid noon sun, check on elders and children.",
}


def show_helplines() -> None:
    for number, who in HELPLINES.items():
        print(f"  {number:>5}  {who}")


def show_tip() -> None:
    kind = input("Disaster (flood/lightning/heatwave): ").strip().lower()
    print("  ", TIPS.get(kind, "No tip yet. Try: " + ", ".join(TIPS)))


def quit_app() -> None:
    raise SystemExit("Stay safe. Goodbye!")


ACTIONS = {
    "1": ("Emergency helplines", show_helplines),
    "2": ("Quick safety tip", show_tip),
    "0": ("Exit", quit_app),
}


def main() -> None:
    while True:
        print("\n=== AapdaMitra ===")
        for key, (label, _) in ACTIONS.items():
            print(f" {key}. {label}")
        choice = input("Choose: ").strip()
        action = ACTIONS.get(choice)
        if action:
            action[1]()
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
