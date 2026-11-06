"""day-01: AapdaMitra while-loop menu."""

SAMPLE_QUESTIONS = [
    "What should my family do BEFORE a flood?",
    "Is it safe to walk through flood water?",
    "How do I protect my family during a heatwave?",
]


def about():
    print("\nAapdaMitra gives NDMA's official do's and don'ts for floods,")
    print("heatwaves and earthquakes, for village families near the Godavari.")


def sample_questions():
    print("\nQuestions AapdaMitra can answer:")
    for i, q in enumerate(SAMPLE_QUESTIONS, 1):
        print(f"  {i}. {q}")


def heat_check():
    """One if/elif rule. A simple demo, NOT IMD's official heatwave criteria."""
    raw = input("\nToday's temperature in °C: ").strip()
    try:
        temp = float(raw)
    except ValueError:
        print("Please type a number, for example 41.")
        return

    if temp >= 45:
        print("SEVERE heat: stay indoors, drink water often, call 108 if anyone is ill.")
    elif temp >= 40:
        print("Heatwave conditions: avoid the sun from 12 to 3 pm, drink water often.")
    elif temp >= 37:
        print("Very hot: carry water, wear light cotton clothes, rest in shade.")
    else:
        print("No heat alert, but keep drinking water.")


running = True
while running:
    print("\n--- AapdaMitra ---")
    print("1. About AapdaMitra")
    print("2. Sample questions")
    print("3. Heat check")
    print("0. Exit")
    choice = input("Choose: ").strip()

    if choice == "1":
        about()
    elif choice == "2":
        sample_questions()
    elif choice == "3":
        heat_check()
    elif choice == "0":
        print("Stay safe!")
        running = False
    else:
        print("Invalid choice, try again.")
