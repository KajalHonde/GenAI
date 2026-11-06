# Day 01 - AapdaMitra Menu

while True:
    print("\n========== AAPDAMITRA MENU ==========")
    print("1. About AapdaMitra")
    print("2. Sample Questions")
    print("3. Disaster Safety Rule Check")
    print("0. Exit")
    print("=====================================")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("\nAbout AapdaMitra")
        print("AapdaMitra helps families prepare for floods, heatwaves and earthquakes.")
        print("It provides safety information before, during and after disasters.")

    elif choice == "2":
        print("\nSample Questions:")
        print("1. What should we do before a flood?")
        print("2. How can we stay safe during a heatwave?")
        print("3. What should we do during an earthquake?")

    elif choice == "3":
        hazard = input("Enter hazard (flood/heatwave/earthquake): ").strip().lower()
        phase = input("Enter phase (before/during/after): ").strip().lower()

        if hazard == "flood" and phase == "before":
            print("Prepare an emergency kit and move important documents to a safe place.")
        elif hazard == "flood" and phase == "during":
            print("Move to higher ground and stay away from floodwater.")
        elif hazard == "flood" and phase == "after":
            print("Return only when authorities say it is safe; avoid contaminated water.")
        elif hazard == "heatwave" and phase == "before":
            print("Keep drinking water available and plan to limit outdoor activity.")
        elif hazard == "heatwave" and phase == "during":
            print("Stay in a cool or shaded place and drink water regularly.")
        elif hazard == "heatwave" and phase == "after":
            print("Continue hydration and seek medical help if heat-illness symptoms persist.")
        elif hazard == "earthquake" and phase == "before":
            print("Secure heavy furniture and identify safe places in each room.")
        elif hazard == "earthquake" and phase == "during":
            print("Drop, Cover, and Hold On. Stay away from windows.")
        elif hazard == "earthquake" and phase == "after":
            print("Check for injuries, expect aftershocks, and follow official instructions.")
        else:
            print("Invalid hazard or phase. Use the listed options.")

    elif choice == "0":
        print("Thank you for using AapdaMitra!")
        print("Stay Safe, Stay Prepared!")
        break

    else:
        print("Invalid choice. Please try again.")
