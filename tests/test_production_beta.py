import subprocess
import unittest

from tools.check_production_beta import REQUIRED_ARTIFACTS, check_production_beta
from tools.completion import (
    FLAGSHIP_CHAIN,
    LIFECYCLE_CHAIN,
    PRODUCTION_BETA_PATTERNS,
    PRODUCTION_BETA_STATUSES,
    STABLE_DEVICE_CONVEYOR_CHAIN,
    STABLE_STATUS,
)
from tools.patternlib import pattern_index, validate_all


class ProductionBetaTests(unittest.TestCase):
    def test_declared_production_beta_patterns_use_allowed_statuses(self) -> None:
        patterns = validate_all()
        for pattern in patterns:
            if pattern.id in PRODUCTION_BETA_PATTERNS:
                self.assertIn(pattern.id, PRODUCTION_BETA_PATTERNS)
                self.assertIn(pattern.data["status"], PRODUCTION_BETA_STATUSES)

    def test_required_artifacts_are_declared_and_present(self) -> None:
        patterns = validate_all()
        check_production_beta(patterns)
        index = pattern_index(patterns)
        for pattern_id, relpaths in REQUIRED_ARTIFACTS.items():
            pattern = index[pattern_id]
            declared = {
                relpath
                for artifact_paths in pattern.data["artifacts"].values()
                for relpath in artifact_paths
            }
            self.assertTrue(relpaths <= declared)
            for relpath in relpaths:
                self.assertTrue((pattern.path.parent / relpath).exists())

    def test_install_scripts_default_to_dry_run(self) -> None:
        patterns = pattern_index(validate_all())
        for pattern_id in FLAGSHIP_CHAIN:
            script = patterns[pattern_id].path.parent / "scripts" / "install.sh"
            result = subprocess.run([str(script), "--help"], text=True, capture_output=True, check=True)
            self.assertIn("--apply", result.stdout)
            self.assertIn("dry-run", result.stdout.lower())

        for pattern_id in PRODUCTION_BETA_PATTERNS - FLAGSHIP_CHAIN:
            script = patterns[pattern_id].path.parent / "scripts" / "install.sh"
            result = subprocess.run([str(script), "--help"], text=True, capture_output=True, check=True)
            self.assertIn("--apply", result.stdout)
            self.assertIn("dry-run", result.stdout.lower())

    def test_production_beta_patterns_declare_lifecycle_metadata(self) -> None:
        patterns = pattern_index(validate_all())
        for pattern_id in PRODUCTION_BETA_PATTERNS:
            lifecycle = patterns[pattern_id].data.get("lifecycle")
            self.assertIsInstance(lifecycle, dict)
            self.assertTrue({"dry_run", "staged_root"} & set(lifecycle["install_modes"]))
            self.assertTrue({"mock", "staged_root"} & set(lifecycle["doctor_modes"]))

    def test_managed_lifecycle_patterns_have_rollback_and_uninstall(self) -> None:
        patterns = pattern_index(validate_all())
        for pattern_id in LIFECYCLE_CHAIN:
            pattern = patterns[pattern_id]
            self.assertTrue(pattern.data["lifecycle"]["managed"])
            declared = {
                relpath
                for artifact_paths in pattern.data["artifacts"].values()
                for relpath in artifact_paths
            }
            self.assertIn("scripts/rollback.sh", declared)
            self.assertIn("scripts/uninstall.sh", declared)

        for pattern_id in STABLE_DEVICE_CONVEYOR_CHAIN:
            pattern = patterns[pattern_id]
            self.assertEqual(pattern.data["status"], STABLE_STATUS)
            self.assertTrue(pattern.data["lifecycle"]["managed"])


if __name__ == "__main__":
    unittest.main()
