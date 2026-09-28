"""Generate a synthetic four-table insurance source system."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


RNG = np.random.default_rng(42)
N = 4085


def ownership_patterns() -> list[tuple[int, int, int]]:
    counts = {
        (1, 0, 0): 782,
        (0, 1, 0): 98,
        (0, 0, 1): 65,
        (1, 1, 0): 1000,
        (1, 0, 1): 600,
        (0, 1, 1): 465,
        (1, 1, 1): 975,
        (0, 0, 0): 100,
    }
    values = [pattern for pattern, count in counts.items() for _ in range(count)]
    RNG.shuffle(values)
    return values


patterns = ownership_patterns()
motor_flag = np.array([row[0] for row in patterns])
health_flag = np.array([row[1] for row in patterns])
travel_flag = np.array([row[2] for row in patterns])

age_groups = RNG.choice(
    ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
    size=N,
    p=[0.3043, 0.055, 0.06, 0.4931, 0.05, 0.0376],
)
age_ranges = {
    "18-24": (18, 24), "25-34": (25, 34), "35-44": (35, 44),
    "45-54": (45, 54), "55-64": (55, 64), "65+": (65, 79),
}
age = np.array([RNG.integers(*((low, high + 1))) for low, high in map(age_ranges.get, age_groups)])
location = RNG.choice(["Urban", "Rural"], N, p=[0.5684, 0.4316])

channel = []
for person_age, person_location in zip(age, location):
    if person_age <= 34:
        probabilities = [0.58, 0.14, 0.28]
    elif person_age >= 55:
        probabilities = [0.22, 0.70, 0.08]
    else:
        probabilities = [0.45, 0.42, 0.13]
    if person_location == "Rural":
        probabilities = np.array(probabilities) + np.array([-0.05, 0.08, -0.03])
    channel.append(RNG.choice(["Email", "Phone", "SMS"], p=np.array(probabilities) / np.sum(probabilities)))

customer_ids = np.arange(100001, 100001 + N)
motor_ids = np.where(motor_flag == 1, [f"M{index:05d}" for index in customer_ids], None)
health_ids = np.where(health_flag == 1, [f"H{index:05d}" for index in customer_ids], None)
travel_ids = np.where(travel_flag == 1, [f"T{index:05d}" for index in customer_ids], None)

customers = pd.DataFrame(
    {
        "CustomerID": customer_ids,
        "Age": age,
        "Gender": RNG.choice(["Female", "Male", "Non-binary"], N, p=[0.5, 0.49, 0.01]),
        "Location": location,
        "ComChannel": channel,
        "DependentChildren": np.where(age >= 28, RNG.poisson(1.1, N), RNG.binomial(1, 0.08, N)),
        "MotorID": motor_ids,
        "HealthID": health_ids,
        "TravelID": travel_ids,
    }
)

motor = pd.DataFrame(
    {
        "MotorID": customers.loc[motor_flag == 1, "MotorID"],
        "MotorType": RNG.choice(["Comprehensive", "Third Party", "Telematics"], motor_flag.sum(), p=[0.55, 0.30, 0.15]),
        "MotorAnnualPremium": RNG.integers(280, 1250, motor_flag.sum()),
    }
)
health = pd.DataFrame(
    {
        "HealthID": customers.loc[health_flag == 1, "HealthID"],
        "HealthType": RNG.choice(["Core", "Enhanced", "Family"], health_flag.sum(), p=[0.42, 0.32, 0.26]),
        "HealthAnnualPremium": RNG.integers(350, 1850, health_flag.sum()),
    }
)
travel = pd.DataFrame(
    {
        "TravelID": customers.loc[travel_flag == 1, "TravelID"],
        "TravelType": RNG.choice(["Single Trip", "Annual", "Family"], travel_flag.sum(), p=[0.46, 0.39, 0.15]),
        "TravelAnnualPremium": RNG.integers(45, 420, travel_flag.sum()),
    }
)

directory = Path("data/demo")
directory.mkdir(parents=True, exist_ok=True)
for name, frame in {
    "customers": customers,
    "motor_policies": motor,
    "health_policies": health,
    "travel_policies": travel,
}.items():
    frame.to_csv(directory / f"{name}.csv", index=False)
    print(f"{name}: {len(frame):,} rows")

