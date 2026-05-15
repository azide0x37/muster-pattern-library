import unittest

from tools.completion import (
    DEVICE_TRIGGERED_CONVEYOR_CHAIN,
    FLAGSHIP_CHAIN,
    HOME_ASSISTANT_CHAIN,
    LIFECYCLE_CHAIN,
    PRODUCTION_BETA_STATUSES,
    STABLE_DEVICE_CONVEYOR_CHAIN,
    STABLE_STATUS,
    completion_rows,
    grouped_percentages,
    overall_percent,
)
from tools.patternlib import validate_all


class CompletionTests(unittest.TestCase):
    def test_overall_completion_reflects_flagship_status(self) -> None:
        patterns = validate_all()
        self.assertEqual(len(patterns), 34)
        self.assertEqual(overall_percent(patterns), 75.5)

    def test_grouped_completion_scores(self) -> None:
        groups = grouped_percentages(validate_all())
        self.assertEqual(groups[(1, "common")], 100.0)
        self.assertEqual(groups[(1, "rare")], 100.0)
        self.assertEqual(groups[(1, "mythic")], 100.0)
        self.assertEqual(groups[(2, "common")], 68.0)
        self.assertEqual(groups[(2, "rare")], 58.7)
        self.assertEqual(groups[(3, "common")], 76.7)

    def test_flagship_rows_are_production_beta(self) -> None:
        rows = {row.pattern_id: row for row in completion_rows(validate_all())}
        self.assertEqual(set(rows).intersection(FLAGSHIP_CHAIN), FLAGSHIP_CHAIN)
        for pattern_id in FLAGSHIP_CHAIN:
            row = rows[pattern_id]
            self.assertIn(
                {"implementation": row.implementation, "docs": row.docs, "tests": row.tests},
                PRODUCTION_BETA_STATUSES,
            )
            self.assertIn(row.percent, {76.7, 100.0})

    def test_device_conveyor_rows_are_production_beta(self) -> None:
        rows = {row.pattern_id: row for row in completion_rows(validate_all())}
        self.assertEqual(set(rows).intersection(DEVICE_TRIGGERED_CONVEYOR_CHAIN), DEVICE_TRIGGERED_CONVEYOR_CHAIN)
        for pattern_id in DEVICE_TRIGGERED_CONVEYOR_CHAIN:
            row = rows[pattern_id]
            self.assertEqual((row.implementation, row.docs, row.tests), ("stable", "stable", "stable"))
            self.assertEqual(row.percent, 100.0)

    def test_lifecycle_rows_are_production_beta(self) -> None:
        rows = {row.pattern_id: row for row in completion_rows(validate_all())}
        self.assertEqual(set(rows).intersection(LIFECYCLE_CHAIN), LIFECYCLE_CHAIN)
        for pattern_id in LIFECYCLE_CHAIN:
            row = rows[pattern_id]
            self.assertIn(
                {"implementation": row.implementation, "docs": row.docs, "tests": row.tests},
                PRODUCTION_BETA_STATUSES,
            )
            self.assertIn(row.percent, {76.7, 100.0})

    def test_home_assistant_rows_are_production_beta(self) -> None:
        rows = {row.pattern_id: row for row in completion_rows(validate_all())}
        self.assertEqual(set(rows).intersection(HOME_ASSISTANT_CHAIN), HOME_ASSISTANT_CHAIN)
        for pattern_id in HOME_ASSISTANT_CHAIN:
            row = rows[pattern_id]
            self.assertIn(
                {"implementation": row.implementation, "docs": row.docs, "tests": row.tests},
                PRODUCTION_BETA_STATUSES,
            )
            self.assertEqual(row.percent, 76.7)

    def test_all_tech_1_rows_are_complete(self) -> None:
        rows = completion_rows(validate_all())
        for row in rows:
            if row.tech_level == 1:
                self.assertEqual(
                    {"implementation": row.implementation, "docs": row.docs, "tests": row.tests},
                    STABLE_STATUS,
                )
                self.assertEqual(row.percent, 100.0)

    def test_stable_device_conveyor_rows_are_complete(self) -> None:
        rows = {row.pattern_id: row for row in completion_rows(validate_all())}
        self.assertEqual(set(rows).intersection(STABLE_DEVICE_CONVEYOR_CHAIN), STABLE_DEVICE_CONVEYOR_CHAIN)
        for pattern_id in STABLE_DEVICE_CONVEYOR_CHAIN:
            row = rows[pattern_id]
            self.assertEqual((row.implementation, row.docs, row.tests), ("stable", "stable", "stable"))
            self.assertEqual(row.percent, 100.0)


if __name__ == "__main__":
    unittest.main()
