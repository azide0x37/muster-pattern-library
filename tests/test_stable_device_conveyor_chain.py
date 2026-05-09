import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
R2 = ROOT / "patterns/t1/rare/R2.device-binding"
R5 = ROOT / "patterns/t1/rare/R5.capability-mount"
T2R4 = ROOT / "patterns/t2/rare/T2R4.device-triggered-conveyor"
WAIT_SCRIPT = ROOT / "patterns/t2/common/T2C1.hot-cold-nas-conveyor/scripts/wait-for-hot-capacity.sh"


def run_script(script: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    full_env.update(env)
    return subprocess.run([str(script), *args], cwd=ROOT, env=full_env, text=True, capture_output=True, check=True)


def run_script_no_check(script: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    full_env.update(env)
    return subprocess.run([str(script), *args], cwd=ROOT, env=full_env, text=True, capture_output=True)


def assert_lifecycle(test: unittest.TestCase, pattern_dir: Path, env: dict[str, str], artifact: Path, config: Path, ledger: Path) -> None:
    install = pattern_dir / "scripts/install.sh"
    rollback = pattern_dir / "scripts/rollback.sh"
    uninstall = pattern_dir / "scripts/uninstall.sh"

    run_script(install, "--apply", env=env)
    config.write_text(config.read_text() + "\nUSER_SETTING=kept\n")
    artifact.write_text("previous artifact\n")
    run_script(install, "--apply", env=env)
    test.assertIn("USER_SETTING=kept", config.read_text())
    test.assertNotEqual(artifact.read_text(), "previous artifact\n")

    run_script(rollback, "--apply", env=env)
    test.assertEqual(artifact.read_text(), "previous artifact\n")

    run_script(uninstall, "--apply", env=env)
    test.assertFalse(artifact.exists())
    test.assertTrue(config.exists())
    test.assertTrue(ledger.exists())


class StableDeviceConveyorChainTests(unittest.TestCase):
    def test_r2_helper_json_and_udev_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {"MUSTER_MOCK_ROOT": tmp}
            run_script(R2 / "scripts/device-bound-run.sh", "/dev/sr0", env=env)
            data = json.loads((Path(tmp) / "run/muster/device-binding.json").read_text())
            self.assertEqual(data["device"], "/dev/sr0")
            self.assertEqual(data["trigger"], "udev-systemd")

        rule = (R2 / "udev/90-muster-device-binding.rules").read_text()
        self.assertIn("SYSTEMD_WANTS", rule)
        self.assertNotIn("RUN+=", rule)

    def test_r2_lifecycle_is_idempotent_and_artifact_only_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {"MUSTER_ROOT": tmp}
            assert_lifecycle(
                self,
                R2,
                env,
                root / "usr/local/lib/muster/device-bound-run.sh",
                root / "etc/muster/device-binding.env",
                root / "var/lib/muster/lifecycle/R2.device-binding",
            )

    def test_r5_capability_states_and_sanitized_status_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {"MUSTER_MOCK_ROOT": tmp}
            run_script(R5 / "scripts/check-capability.sh", "cold/storage?bad", "/mnt/muster/cold", env=env)
            status = root / "run/muster/capability-coldstoragebad.json"
            self.assertTrue(status.exists())
            self.assertEqual(json.loads(status.read_text())["state"], "healthy")

            missing = run_script_no_check(
                R5 / "scripts/check-capability.sh",
                "missing",
                str(root / "does-not-exist"),
                "--apply",
                env={"STATE_ROOT": str(root / "run/muster")},
            )
            self.assertEqual(missing.returncode, 1)
            self.assertEqual(json.loads((root / "run/muster/capability-missing.json").read_text())["reason"], "missing_path")

            if subprocess.run(["sh", "-c", "command -v findmnt"], capture_output=True).returncode == 0:
                path = root / "not-mounted"
                path.mkdir()
                degraded = run_script_no_check(
                    R5 / "scripts/check-capability.sh",
                    "not-mounted",
                    str(path),
                    "--apply",
                    env={"STATE_ROOT": str(root / "run/muster")},
                )
                self.assertEqual(degraded.returncode, 75)

    def test_r5_lifecycle_is_idempotent_and_artifact_only_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {"MUSTER_ROOT": tmp}
            assert_lifecycle(
                self,
                R5,
                env,
                root / "usr/local/lib/muster/check-capability.sh",
                root / "etc/muster/capability-mount.env",
                root / "var/lib/muster/lifecycle/R5.capability-mount",
            )

    def test_t2r4_lifecycle_is_idempotent_and_artifact_only_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {"MUSTER_ROOT": tmp}
            assert_lifecycle(
                self,
                T2R4,
                env,
                root / "usr/local/lib/muster/device-convey.sh",
                root / "etc/muster/device-conveyor.env",
                root / "var/lib/muster/lifecycle/T2R4.device-triggered-conveyor",
            )
            self.assertFalse((root / "usr/local/lib/muster/convey").exists())
            self.assertFalse((root / "usr/local/lib/muster/wait-for-hot-capacity.sh").exists())

    def test_t2r4_missing_capability_fails_before_ingest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script_no_check(
                T2R4 / "scripts/device-convey.sh",
                "/dev/sr0",
                env={"MUSTER_MOCK_ROOT": tmp, "MUSTER_SKIP_MOCK_CAPABILITY_CREATE": "1"},
            )
            self.assertEqual(result.returncode, 1)
            data = json.loads((Path(tmp) / "run/muster/device-conveyor.json").read_text())
            self.assertEqual(data["reason"], "capability_unavailable")

    def test_t2r4_capacity_timeout_fails_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script_no_check(
                T2R4 / "scripts/device-convey.sh",
                "/dev/sr0",
                env={
                    "MUSTER_MOCK_ROOT": tmp,
                    "WAIT_FOR_HOT_CAPACITY": str(WAIT_SCRIPT),
                    "MUSTER_MOCK_BACKPRESSURE": "1",
                    "MIN_HOT_FREE_BYTES": "1",
                    "CAPACITY_TIMEOUT_SECONDS": "1",
                    "CAPACITY_INTERVAL_SECONDS": "1",
                },
            )
            self.assertEqual(result.returncode, 75)
            data = json.loads((Path(tmp) / "run/muster/hot-capacity.json").read_text())
            self.assertEqual(data["reason"], "capacity_timeout")

    def test_t2r4_ingest_failure_leaves_failed_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script_no_check(
                T2R4 / "scripts/device-convey.sh",
                "/dev/sr0",
                env={
                    "MUSTER_MOCK_ROOT": tmp,
                    "WAIT_FOR_HOT_CAPACITY": str(WAIT_SCRIPT),
                    "MIN_HOT_FREE_BYTES": "1",
                    "INGEST_COMMAND": "printf failed > \"$RUN_DIR/output.txt\"; exit 42",
                },
            )
            self.assertEqual(result.returncode, 1)
            work_root = Path(tmp) / "var/lib/muster/device-conveyor/work"
            failed = list(work_root.glob("*/.ingest-failed"))
            self.assertEqual(len(failed), 1)

    def test_t2r4_lock_contention_degrades(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock_dir = Path(tmp) / "run/muster/device-conveyor.lockdir"
            lock_dir.mkdir(parents=True)
            result = run_script_no_check(
                T2R4 / "scripts/device-convey.sh",
                "/dev/sr0",
                env={"MUSTER_MOCK_ROOT": tmp, "MUSTER_FORCE_LOCKDIR": "1"},
            )
            self.assertEqual(result.returncode, 75)
            data = json.loads((Path(tmp) / "run/muster/device-conveyor.json").read_text())
            self.assertEqual(data["reason"], "already_running")


if __name__ == "__main__":
    unittest.main()
