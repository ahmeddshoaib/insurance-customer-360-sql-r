"""Build and validate the synthetic Customer 360 with DuckDB."""

from __future__ import annotations

from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "demo"
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)

connection = duckdb.connect()
for table in ("customers", "motor_policies", "health_policies", "travel_policies"):
    connection.execute(
        f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{DATA / f'{table}.csv'}', nullstr='')"
    )

for table, key in {
    "customers": "CustomerID",
    "motor_policies": "MotorID",
    "health_policies": "HealthID",
    "travel_policies": "TravelID",
}.items():
    total, distinct = connection.execute(f"SELECT COUNT(*), COUNT(DISTINCT {key}) FROM {table}").fetchone()
    if total != distinct:
        raise AssertionError(f"Duplicate primary keys in {table}")

connection.execute((ROOT / "sql" / "01_build_customer_360.sql").read_text())
connection.execute(f"COPY customer_360 TO '{OUTPUT / 'customer_360.csv'}' (HEADER, DELIMITER ',')")

summary = connection.execute(
    """
    SELECT
        'synthetic_demo' AS data_label,
        COUNT(*) AS total_customers,
        SUM(HasMotor) AS motor_customers,
        SUM(HasHealth) AS health_customers,
        SUM(HasTravel) AS travel_customers,
        SUM(PolicyCount = 3) AS triple_policy_customers,
        SUM(PolicyCount = 0) AS no_policy_customers
    FROM customer_360
    """
).df()
summary.to_csv(OUTPUT / "portfolio_summary.csv", index=False)

channel = connection.execute(
    """
    SELECT AgeGroup, Location, ComChannel, COUNT(*) AS customers
    FROM customer_360
    GROUP BY ALL
    ORDER BY AgeGroup, Location, customers DESC
    """
).df()
channel.insert(0, "data_label", "synthetic_demo")
channel.to_csv(OUTPUT / "channel_by_age_location.csv", index=False)

expected = (4085, 3357, 2538, 2105, 975, 100)
observed = tuple(int(summary.iloc[0][column]) for column in summary.columns[1:])
if observed != expected:
    raise AssertionError(f"Unexpected synthetic control totals: {observed}")

print(summary.to_string(index=False))
print("CUSTOMER 360 BUILD PASSED")

