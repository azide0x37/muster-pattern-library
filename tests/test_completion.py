import unittest

from tools.completion import FLAGSHIP_CHAIN, completion_rows, grouped_percentages, overall_percent
from tools.patternlib import validate_all


class CompletionTests(unittest.TestCase):
    def test_overall_completion_reflects_flagship_status(self) -> None:
        patterns = validate_all()
        self.assertEqual(len(patterns), 30)
        self.assertEqual(overall_percent(patterns), 46.1)

    def test_grouped_completion_scores(self) -> None:
        groups = grouped_percentages(validate_all())
        self.assertEqual(groups[(1, "common")], 68.0)
        self.assertEqual(groups[(2, "common")], 68.0)
        self.assertEqual(groups[(3, "common")], 76.7)
        self.assertEqual(groups[(1, "rare")], 33.0)

    def test_flagship_rows_are_production_beta(self) -> None:
        rows = {row.pattern_id: row for row in completion_rows(validate_all())}
        self.assertEqual(set(rows).intersection(FLAGSHIP_CHAIN), FLAGSHIP_CHAIN)
        for pattern_id in FLAGSHIP_CHAIN:
            row = rows[pattern_id]
            self.assertEqual((row.implementation, row.docs, row.tests), ("usable", "reviewed", "reviewed"))
            self.assertEqual(row.percent, 76.7)


if __name__ == "__main__":
    unittest.main()
