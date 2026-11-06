"""day-01: AapdaMitra project card + greeting."""

product = "AapdaMitra"
hazards = ["flood", "heatwave", "earthquake"]
user = "gram panchayat member, Godavari bank near Kopargaon"
source = "NDMA do's and don'ts and guidelines (ndma.gov.in)"

print("=" * 60)
print(f"  {product}  (आपदा मित्र)")
print("=" * 60)
print(f"Product : what to do before, during and after a {', '.join(hazards)}")
print(f"User    : {user}")
print(f"Source  : {source}")
print("-" * 60)

name = input("What is your name? ").strip() or "Friend"
village = input("Which village are you from? ").strip() or "your village"

print(f"\nNamaste {name}! {product} will help {village} prepare for")
print(f"monsoon floods (June-September) and the April-May heatwave.")
print("Emergency? Call 112.")
