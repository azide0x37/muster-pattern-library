import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.check_stable_tech1 import check_stable_tech1
from tools.patternlib import pattern_index, validate_all


ROOT = Path(__file__).resolve().parents[1]


def run_script(script: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    full_env.update(env)
    return subprocess.run([str(script), *args], cwd=ROOT, env=full_env, text=True, capture_output=True, check=True)


def run_script_no_check(script: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    full_env.update(env)
    return subprocess.run([str(script), *args], cwd=ROOT, env=full_env, text=True, capture_output=True)


class StableTech1PatternTests(unittest.TestCase):
    def test_stable_tech1_gate_passes(self) -> None:
        check_stable_tech1(validate_all())

    def test_service_capsule_doctor_verifies_staged_unit(self) -> None:
        pattern = ROOT / "patterns/t1/common/C1.service-capsule"
        doctor = pattern / "scripts/doctor.sh"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            fake_systemd_analyze = bin_dir / "systemd-analyze"
            fake_systemd_analyze.write_text(
                "#!/usr/bin/env sh\n"
                "set -eu\n"
                "test \"$1\" = verify\n"
                "unit=\"$2\"\n"
                "! grep -q 'Documentation=file:README.md' \"$unit\"\n"
                "! grep -q '/usr/local/lib/muster/service-capsule-run.sh' \"$unit\"\n"
                "grep -q 'Documentation=file:/.*/README.md' \"$unit\"\n"
                "grep -q '/scripts/service-capsule-run.sh --apply' \"$unit\"\n"
            )
            fake_systemd_analyze.chmod(0o755)
            run_script(
                doctor,
                env={
                    "MUSTER_MOCK_ROOT": str(root / "mock"),
                    "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                },
            )

    def test_dropfolder_processes_and_records_failures(self) -> None:
        pattern = ROOT / "patterns/t1/common/C3.dropfolder-trigger"
        script = pattern / "scripts/dropfolder-process.sh"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inbox = root / "var/lib/muster/dropfolder/inbox"
            inbox.mkdir(parents=True)
            (inbox / "job.txt").write_text("payload\n")
            run_script(script, "--once", env={"MUSTER_MOCK_ROOT": tmp})
            self.assertEqual((root / "var/lib/muster/dropfolder/done/job.txt").read_text(), "payload\n")
            status = json.loads((root / "run/muster/dropfolder-trigger.json").read_text())
            self.assertEqual(status["processed"], 1)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inbox = root / "var/lib/muster/dropfolder/inbox"
            inbox.mkdir(parents=True)
            (inbox / "bad.txt").write_text("payload\n")
            result = run_script_no_check(script, "--once", env={"MUSTER_MOCK_ROOT": tmp, "DROPFOLDER_FORCE_FAIL": "1"})
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((root / "var/lib/muster/dropfolder/failed/bad.txt").exists())

    def test_rare_helpers_emit_status(self) -> None:
        patterns = pattern_index(validate_all())
        cases = [
            ("R1.socket-anteroom", "socket-anteroom-serve.sh", "socket-anteroom.json"),
            ("R3.cgroup-governor", "cgroup-governed-run.sh", "cgroup-governor.json"),
            ("R4.state-ledger", "state-ledger-write.sh", "state-ledger.json"),
        ]
        for pattern_id, script_name, status_name in cases:
            with self.subTest(pattern_id=pattern_id), tempfile.TemporaryDirectory() as tmp:
                script = patterns[pattern_id].path.parent / "scripts" / script_name
                run_script(script, env={"MUSTER_MOCK_ROOT": tmp})
                self.assertTrue((Path(tmp) / "run/muster" / status_name).exists())

    def test_mythic_helpers_handle_failure_modes(self) -> None:
        patterns = pattern_index(validate_all())

        with tempfile.TemporaryDirectory() as tmp:
            fact_dir = Path(tmp) / "run/muster/local-truth/facts"
            fact_dir.mkdir(parents=True)
            (fact_dir / "bad.json").write_text('{"state":"failed"}\n')
            script = patterns["M1.local-truth-sheaf"].path.parent / "scripts/local-truth-reduce.sh"
            result = run_script_no_check(script, env={"MUSTER_MOCK_ROOT": tmp})
            self.assertNotEqual(result.returncode, 0)
            status = json.loads((Path(tmp) / "run/muster/local-truth-sheaf.json").read_text())
            self.assertEqual(status["state"], "failed")

        with tempfile.TemporaryDirectory() as tmp:
            script = patterns["M2.holonomy-detector"].path.parent / "scripts/holonomy-check.sh"
            result = run_script_no_check(script, env={"MUSTER_MOCK_ROOT": tmp, "HOLONOMY_STEPS": "idle mounted checked"})
            self.assertEqual(result.returncode, 75)

        with tempfile.TemporaryDirectory() as tmp:
            script = patterns["M3.simplicial-task-graph"].path.parent / "scripts/task-graph-evaluate.sh"
            result = run_script_no_check(
                script,
                env={"MUSTER_MOCK_ROOT": tmp, "REQUIRED_FACES": "input worker output", "PRESENT_FACES": "input output"},
            )
            self.assertEqual(result.returncode, 75)
            status = json.loads((Path(tmp) / "run/muster/simplicial-task-graph.json").read_text())
            self.assertEqual(status["missing"], "worker")

        with tempfile.TemporaryDirectory() as tmp:
            script = patterns["M4.local-topos-runtime"].path.parent / "scripts/topos-evaluate.sh"
            missing = Path(tmp) / "missing"
            result = run_script_no_check(script, "--evidence", str(missing), env={"MUSTER_MOCK_ROOT": tmp})
            self.assertNotEqual(result.returncode, 0)

        with tempfile.TemporaryDirectory() as tmp:
            script = patterns["M5.temporal-sheaf"].path.parent / "scripts/temporal-sheaf-run.sh"
            run_script(script, env={"MUSTER_MOCK_ROOT": tmp})
            run_script(script, env={"MUSTER_MOCK_ROOT": tmp})
            status = json.loads((Path(tmp) / "run/muster/temporal-sheaf.json").read_text())
            self.assertEqual(status["carried_obligations"], 2)


if __name__ == "__main__":
    unittest.main()
