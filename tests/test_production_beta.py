import subprocess
import unittest

from tools.check_production_beta import REQUIRED_ARTIFACTS, check_production_beta
from tools.completion import FLAGSHIP_CHAIN, PRODUCTION_BETA_STATUS
from tools.patternlib import pattern_index, validate_all


class ProductionBetaTests(unittest.TestCase):
    def test_only_flagship_patterns_claim_production_beta_status(self) -> None:
        patterns = validate_all()
        for pattern in patterns:
            if pattern.data["status"] == PRODUCTION_BETA_STATUS:
                self.assertIn(pattern.id, FLAGSHIP_CHAIN)

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


if __name__ == "__main__":
    unittest.main()
