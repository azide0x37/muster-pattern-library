import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
C6 = ROOT / "patterns/t1/common/C6.lifecycle-capsule"
T2R5 = ROOT / "patterns/t2/rare/T2R5.signed-update-rail"


def run_script(script: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    full_env.update(env)
    return subprocess.run([str(script), *args], cwd=ROOT, env=full_env, text=True, capture_output=True, check=True)


def make_release(root: Path, version: str, doctor_exit: int) -> tuple[Path, str]:
    package_parent = root / f"pkg-{version}"
    package_dir = package_parent / f"muster-lifecycle-test-{version}"
    bin_dir = package_dir / "bin"
    bin_dir.mkdir(parents=True)
    doctor = bin_dir / "doctor.sh"
    doctor.write_text(f"#!/usr/bin/env sh\nexit {doctor_exit}\n")
    doctor.chmod(0o755)

    artifact = root / f"muster-lifecycle-test-{version}.tar.gz"
    with tarfile.open(artifact, "w:gz") as archive:
        archive.add(package_dir, arcname=package_dir.name)
    sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    return artifact, sha


class LifecyclePatternTests(unittest.TestCase):
    def test_lifecycle_capsule_staged_install_is_idempotent_and_uninstalls_artifacts_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {"MUSTER_ROOT": str(root), "PROJECT": "muster-lifecycle-test", "MUSTER_VERSION": "1.0.0"}
            install = C6 / "scripts/install.sh"

            run_script(install, "--apply", env=env)
            config = root / "etc/muster-lifecycle-test/muster-lifecycle-test.env"
            config.write_text(config.read_text() + "\nUSER_SETTING=kept\n")

            run_script(install, "--apply", env=env)
            self.assertIn("USER_SETTING=kept", config.read_text())
            self.assertEqual(os.readlink(root / "opt/muster-lifecycle-test/current"), "releases/1.0.0")

            run_script(install, "--apply", env={**env, "MUSTER_VERSION": "1.1.0"})
            self.assertEqual(os.readlink(root / "opt/muster-lifecycle-test/current"), "releases/1.1.0")
            run_script(C6 / "scripts/rollback.sh", "--apply", env={"MUSTER_ROOT": str(root), "PROJECT": "muster-lifecycle-test"})
            self.assertEqual(os.readlink(root / "opt/muster-lifecycle-test/current"), "releases/1.0.0")

            run_script(C6 / "scripts/uninstall.sh", "--apply", env={"MUSTER_ROOT": str(root), "PROJECT": "muster-lifecycle-test"})
            self.assertFalse((root / "opt/muster-lifecycle-test").exists())
            self.assertTrue(config.exists())
            self.assertTrue((root / "var/lib/muster/lifecycle/muster-lifecycle-test").exists())

    def test_signed_update_rail_promotes_and_rolls_back_on_failed_doctor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = "muster-lifecycle-test"
            release = root / f"opt/{project}/releases/1.0.0/bin"
            release.mkdir(parents=True)
            doctor = release / "doctor.sh"
            doctor.write_text("#!/usr/bin/env sh\nexit 0\n")
            doctor.chmod(0o755)
            os.symlink("releases/1.0.0", root / f"opt/{project}/current")

            artifact, sha = make_release(root, "1.1.0", 0)
            manifest = root / "manifest-1.1.0.json"
            manifest.write_text(json.dumps({"version": "1.1.0", "artifact_url": str(artifact), "sha256": sha}))
            env = {"MUSTER_ROOT": str(root), "PROJECT": project}
            run_script(T2R5 / "scripts/update.sh", "--manifest", str(manifest), env=env)
            self.assertEqual(os.readlink(root / f"opt/{project}/current"), "releases/1.1.0")

            artifact, sha = make_release(root, "1.2.0", 1)
            bad_manifest = root / "manifest-1.2.0.json"
            bad_manifest.write_text(json.dumps({"version": "1.2.0", "artifact_url": str(artifact), "sha256": sha}))
            result = subprocess.run(
                [str(T2R5 / "scripts/update.sh"), "--manifest", str(bad_manifest)],
                cwd=ROOT,
                env={**os.environ, **env},
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(os.readlink(root / f"opt/{project}/current"), "releases/1.1.0")

    def test_signed_update_rail_rejects_bad_manifests_and_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = "muster-lifecycle-test"
            release = root / f"opt/{project}/releases/1.0.0/bin"
            release.mkdir(parents=True)
            os.symlink("releases/1.0.0", root / f"opt/{project}/current")
            env = {**os.environ, "MUSTER_ROOT": str(root), "PROJECT": project}

            malformed = root / "malformed.json"
            malformed.write_text(json.dumps({"version": "1.1.0"}))
            result = subprocess.run(
                [str(T2R5 / "scripts/update.sh"), "--manifest", str(malformed)],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)

            artifact, _sha = make_release(root, "1.1.0", 0)
            wrong_hash = root / "wrong-hash.json"
            wrong_hash.write_text(json.dumps({"version": "1.1.0", "artifact_url": str(artifact), "sha256": "0" * 64}))
            result = subprocess.run(
                [str(T2R5 / "scripts/update.sh"), "--manifest", str(wrong_hash)],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(os.readlink(root / f"opt/{project}/current"), "releases/1.0.0")


if __name__ == "__main__":
    unittest.main()
