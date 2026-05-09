import unittest

from tools.patternlib import Pattern, composition_allowed


def make(pattern_id: str, tech_level: int, rarity: str) -> Pattern:
    return Pattern(path=None, data={"id": pattern_id, "tech_level": tech_level, "rarity": rarity})  # type: ignore[arg-type]


class CompositionRuleTests(unittest.TestCase):
    def test_t2_common_can_use_t1_common(self) -> None:
        self.assertTrue(composition_allowed(make("T2C1.x", 2, "common"), make("C1.x", 1, "common")))

    def test_t2_common_cannot_use_t1_rare(self) -> None:
        self.assertFalse(composition_allowed(make("T2C1.x", 2, "common"), make("R1.x", 1, "rare")))

    def test_t3_mythic_can_use_t3_rare(self) -> None:
        self.assertTrue(composition_allowed(make("T3M1.x", 3, "mythic"), make("T3R1.x", 3, "rare")))

    def test_t3_mythic_cannot_use_t3_mythic(self) -> None:
        self.assertFalse(composition_allowed(make("T3M2.x", 3, "mythic"), make("T3M1.x", 3, "mythic")))


if __name__ == "__main__":
    unittest.main()
