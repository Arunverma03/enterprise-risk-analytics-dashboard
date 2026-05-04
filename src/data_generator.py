import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

cities = {
    "India": ["Mumbai", "Pune", "Delhi", "Bengaluru", "Chennai", "Hyderabad"],
    "USA": ["New York", "Chicago", "Dallas", "San Francisco"],
    "UK": ["London", "Manchester", "Birmingham"],
    "UAE": ["Dubai", "Abu Dhabi"],
    "Singapore": ["Singapore"]
}

coordinates = {
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Delhi": (28.6139, 77.2090),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "New York": (40.7128, -74.0060),
    "Chicago": (41.8781, -87.6298),
    "Dallas": (32.7767, -96.7970),
    "San Francisco": (37.7749, -122.4194),
    "London": (51.5074, -0.1278),
    "Manchester": (53.4808, -2.2426),
    "Birmingham": (52.4862, -1.8904),
    "Dubai": (25.2048, 55.2708),
    "Abu Dhabi": (24.4539, 54.3773),
    "Singapore": (1.3521, 103.8198),
}

categories = {
    "Natural Hazard": ["Flood", "Storm", "Earthquake"],
    "Civil Unrest": ["Protest", "Strike", "Road Blockade"],
    "Infrastructure": ["Power Outage", "Network Failure", "Water Disruption"],
    "Security": ["Crime", "Robbery", "Threat"],
    "Industrial Incident": ["Fire", "Explosion", "Leak"]
}

impact_levels = ["Low", "Medium", "High", "Critical"]

actions = {
    "Low": "Monitor situation and inform local teams",
    "Medium": "Increase monitoring and prepare contingency plan",
    "High": "Notify leadership and activate continuity actions",
    "Critical": "Immediate escalation and crisis response required"
}


def random_date():
    start = datetime(2025, 1, 1)
    end = datetime(2026, 4, 28)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


rows = []

for _ in range(500):
    country = random.choice(list(cities.keys()))
    city = random.choice(cities[country])

    category = random.choice(list(categories.keys()))
    event_type = random.choice(categories[category])

    impact = random.choice(impact_levels)

    date = random_date().strftime("%Y-%m-%d")

    lat, lon = coordinates[city]

    summary = f"{event_type} reported in {city} affecting local operations"

    rows.append({
        "date": date,
        "event_summary": summary,
        "recommended_action": actions[impact],
        "category": category,
        "event_type": event_type,
        "impact_level": impact,
        "country": country,
        "city": city,
        "latitude": lat,
        "longitude": lon
    })

df = pd.DataFrame(rows)

df.to_csv("data/risk_events.csv", index=False)

print("500-row enterprise risk dataset created successfully.")
print("Saved to data/risk_events.csv")