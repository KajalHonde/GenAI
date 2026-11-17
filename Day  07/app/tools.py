
def heat_risk_index(temperature_c: float, humidity: float):
    """
    Calculate the Heat Index using the Rothfusz regression.
    Temperature: Celsius
    Humidity: Relative humidity percentage
    """

    if not -20 <= temperature_c <= 60:
        raise ValueError("Temperature must be between -20 and 60 Celsius.")

    if not 0 <= humidity <= 100:
        raise ValueError("Humidity must be between 0 and 100.")

    # Convert Celsius into Fahrenheit
    temperature_f = (temperature_c * 9 / 5) + 32

    # Initial heat index estimate
    hi = 0.5 * (
        temperature_f + 61.0
        + ((temperature_f - 68.0) * 1.2)
        + (humidity * 0.094)
    )

    hi = (hi + temperature_f) / 2

    # Rothfusz regression
    if hi >= 80:
        t = temperature_f
        r = humidity

        hi = (
            -42.379
            + 2.04901523 * t
            + 10.14333127 * r
            - 0.22475541 * t * r
            - 0.00683783 * t**2
            - 0.05481717 * r**2
            + 0.00122874 * t**2 * r
            + 0.00085282 * t * r**2
            - 0.00000199 * t**2 * r**2
        )

        # Low humidity adjustment
        if r < 13 and 80 <= t <= 112:
            adjustment = (
                (13 - r) / 4
            ) * ((17 - abs(t - 95)) / 17) ** 0.5
            hi -= adjustment

        # High humidity adjustment
        elif r > 85 and 80 <= t <= 87:
            adjustment = (
                (r - 85) / 10
            ) * ((87 - t) / 5)
            hi += adjustment

    # Convert Heat Index into Celsius
    heat_index_c = (hi - 32) * 5 / 9

    # Risk classification
    if hi < 90:
        risk = "caution"
        advice = (
            "Drink water regularly, wear light clothing, "
            "and avoid unnecessary exposure to direct sunlight."
        )

    elif hi < 103:
        risk = "extreme caution"
        advice = (
            "Reduce outdoor physical activity, stay in shade, "
            "drink water frequently, and take cooling breaks."
        )

    else:
        risk = "danger"
        advice = (
            "Avoid outdoor activities, move to a cool place, "
            "and seek medical help immediately if heat illness "
            "or signs of heatstroke occur."
        )

    return {
        "temperature_c": temperature_c,
        "humidity": humidity,
        "feels_like_c": round(heat_index_c, 2),
        "risk_level": risk,
        "advice": advice
    }


# Test the tool
if __name__ == "__main__":

    result = heat_risk_index(40, 60)

    print("\n--- AapdaMitra Heat Risk Report ---")

    for key, value in result.items():
        print(f"{key}: {value}")
