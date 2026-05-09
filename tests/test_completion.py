import unittest

from tools.completion import DEVICE_TRIGGERED_CONVEYOR_CHAIN, FLAGSHIP_CHAIN, completion_rows, grouped_percentages, overall_percent
from tools.patternlib import validate_all


class CompletionTests(unittest.TestCase):
    def test_overall_completion_reflects_flagship_status(self) -> None:
        patterns = validate_all()
        self.assertEqual(len(patterns), 31)
        self.assertEqual(overall_percent(patterns), 49.9)

    def test_grouped_completion_scores(self) -> None:
        groups = grouped_percentages(validate_all())
        self.assertEqual(groups[(1, "common")], 68.0)
        self.assertEqual(groups[(1, "rare")], 50.5)
        self.assertEqual(groups[(2, "common")], 68.0)
        self.assertEqual(groups[(2, "rare")], 43.9)
        self.assertEqual(groups[(3, "common")], 76.7)

    def test_flagship_rows_are_production_beta(self) -> None:
        rows = {row.pattern_id: row for row in completion_rows(validate_all())}
        self.assertEqual(set(rows).intersection(FLAGSHIP_CHAIN), FLAGSHIP_CHAIN)
        for pattern_id in FLAGSHIP_CHAIN:
            row = rows[pattern_id]
            self.assertEqual((row.implementation, row.docs, row.tests), ("usable", "reviewed", "reviewed"))
            self.assertEqual(row.percent, 76.7)

    def test_device_conveyor_rows_are_production_beta(self) -> None:
        rows = {row.pattern_id: row for row in completion_rows(validate_all())}
        self.assertEqual(set(rows).intersection(DEVICE_TRIGGERED_CONVEYOR_CHAIN), DEVICE_TRIGGERED_CONVEYOR_CHAIN)
        for pattern_id in DEVICE_TRIGGERED_CONVEYOR_CHAIN:
            row = rows[pattern_id]
            self.assertEqual((row.implementation, row.docs, row.tests), ("usable", "reviewed", "reviewed"))
            self.assertEqual(row.percent, 76.7)


if __name__ == "__main__":
    unittest.main()
