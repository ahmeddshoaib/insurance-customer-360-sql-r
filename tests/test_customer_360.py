from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd


class Customer360Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.customer = pd.read_csv(Path("outputs/customer_360.csv"))
        cls.summary = pd.read_csv(Path("outputs/portfolio_summary.csv"))

    def test_customer_grain_is_preserved(self) -> None:
        self.assertEqual(len(self.customer), 4085)
        self.assertEqual(self.customer["CustomerID"].nunique(), 4085)

    def test_control_totals(self) -> None:
        row = self.summary.iloc[0]
        self.assertEqual(row["data_label"], "synthetic_demo")
        self.assertEqual(int(row["triple_policy_customers"]), 975)
        self.assertEqual(int(row["motor_customers"]), 3357)
        self.assertEqual(int(row["health_customers"]), 2538)
        self.assertEqual(int(row["travel_customers"]), 2105)

    def test_policy_count_reconciles(self) -> None:
        expected = self.customer[["HasMotor", "HasHealth", "HasTravel"]].sum(axis=1)
        self.assertTrue(expected.equals(self.customer["PolicyCount"]))


if __name__ == "__main__":
    unittest.main()

