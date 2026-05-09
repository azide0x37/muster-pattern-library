import unittest

from tools.patternlib import validate_all


class PatternInventoryTests(unittest.TestCase):
    def test_all_patterns_validate(self) -> None:
        patterns = validate_all()
        self.assertGreaterEqual(len(patterns), 29)

    def test_flagship_pattern_exists(self) -> None:
        ids = {pattern.id for pattern in validate_all()}
        self.assertIn("T3C1.edge-appliance-bundle", ids)
        self.assertIn("T3R1.multi-resource-orchestrator", ids)
        self.assertIn("T3M1.machine-priest", ids)
        self.assertIn("T2R4.device-triggered-conveyor", ids)
        self.assertIn("C6.lifecycle-capsule", ids)
        self.assertIn("T2R5.signed-update-rail", ids)


if __name__ == "__main__":
    unittest.main()
