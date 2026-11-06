"""Day 1 - AapdaMitra intro: a tiny personalised welcome."""
from datetime import datetime

BANNER = r"""
 ╔══════════════════════════════════════╗
 ║   AapdaMitra  (आपदा मित्र)            ║
 ║   Be prepared. Stay safe. Help others ║
 ╚══════════════════════════════════════╝
"""


def greeting(hour: int) -> str:
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def main() -> None:
    print(BANNER)
    name = input("What's your name? ").strip() or "Friend"
    place = input("Which town/village are you in? ").strip() or "your area"
    print(f"\n{greeting(datetime.now().hour)}, {name}!")
    print(f"AapdaMitra will help {place} get ready for floods, heat, lightning and more.")
    print("Emergency? Dial 112 right now.\n")


if __name__ == "__main__":
    main()
