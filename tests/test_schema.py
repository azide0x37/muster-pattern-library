from pathlib import Path
import json
import unittest

from tools.patternlib import PatternError, validate_manifest_shape, Pattern


class SchemaTests(unittest.TestCase):
    def test_schema_file_is_valid_json(self) -> None:
        schema = Path("schemas/pattern.schema.json")
        self.assertEqual(json.loads(schema.read_text())["title"], "Muster Pattern Manifest")

    def test_bad_id_prefix_fails(self) -> None:
        pattern = Pattern(
            path=Path("patterns/t2/common/C1.bad/manifest.yaml"),
            data={
                "id": "C1.bad",
                "name": "Bad",
                "tech_level": 2,
                "rarity": "common",
                "mrl": 8,
                "summary": "Bad prefix.",
                "provides": ["bad"],
                "requires": [],
                "subpatterns": [],
                "composes_with": [],
                "artifacts": {},
                "status": {"implementation": "draft", "docs": "draft", "tests": "draft"},
            },
        )
        with self.assertRaises(PatternError):
            validate_manifest_shape(pattern)


if __name__ == "__main__":
    unittest.main()
