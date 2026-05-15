from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

try:
    from completion import STABLE_STATUS
    from patternlib import ROOT, Pattern, PatternError, validate_all
except ModuleNotFoundError:
    from tools.completion import STABLE_STATUS
    from tools.patternlib import ROOT, Pattern, PatternError, validate_all


FORBIDDEN_MARKERS = [
    "echo muster pattern",
    "placeholder",
]


def _artifact_paths(pattern: Pattern) -> set[Path]:
    paths: set[Path] = {pattern.path.parent / "README.md"}
    for artifact_paths in pattern.data["artifacts"].values():
        for relpath in artifact_paths:
            paths.add(pattern.path.parent / relpath)
    examples = pattern.path.parent / "examples"
    if examples.exists():
        paths.update(path for path in examples.rglob("*") if path.is_file())
    return paths


def _check_no_scaffold_markers(pattern: Pattern) -> None:
    for path in _artifact_paths(pattern):
        if not path.exists() or path.is_dir():
            continue
        text = path.read_text(errors="ignore").lower()
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                raise PatternError(f"{path}: stable Tech 1 artifact contains marker {marker!r}")


def _check_scripts_executable(pattern: Pattern) -> None:
    for relpath in pattern.data["artifacts"].get("scripts", []):
        path = pattern.path.parent / relpath
        if path.suffix == ".sh" and not os.access(path, os.X_OK):
            raise PatternError(f"{path}: stable Tech 1 script must be executable")


def _rewritten_unit(pattern: Pattern, unit: Path) -> str:
    readme = pattern.path.parent / "README.md"
    script_dir = pattern.path.parent / "scripts"
    lines: list[str] = []
    for line in unit.read_text().splitlines():
        if line.startswith("Documentation="):
            lines.append(f"Documentation=file:{readme}")
            continue
        if line.startswith("ExecStart=/usr/local/lib/muster/"):
            match = re.match(r"ExecStart=/usr/local/lib/muster/([^ ]+)(.*)", line)
            if match:
                script = script_dir / match.group(1)
                if script.exists():
                    lines.append(f"ExecStart={script}{match.group(2)}")
                    continue
        lines.append(line)
    return "\n".join(lines) + "\n"


def _verify_units(pattern: Pattern, tmp: Path) -> None:
    if shutil.which("systemd-analyze") is None:
        return

    units: list[Path] = []
    for relpath in pattern.data["artifacts"].get("units", []):
        unit = pattern.path.parent / relpath
        if unit.suffix in {".automount", ".mount", ".path", ".service", ".socket", ".timer"}:
            units.append(unit)
    if not units:
        return

    verify_units: list[str] = []
    for unit in units:
        rewritten = tmp / unit.name
        rewritten.write_text(_rewritten_unit(pattern, unit))
        verify_units.append(str(rewritten))

    result = subprocess.run(
        ["systemd-analyze", "verify", *verify_units],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=20,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise PatternError(f"{pattern.path}: stable Tech 1 unit verification failed: {output}")


def _run_doctor(pattern: Pattern) -> None:
    doctor = pattern.path.parent / "scripts" / "doctor.sh"
    if not doctor.exists():
        raise PatternError(f"{pattern.path}: stable Tech 1 pattern must ship scripts/doctor.sh")
    if not os.access(doctor, os.X_OK):
        raise PatternError(f"{doctor}: stable Tech 1 doctor must be executable")

    with tempfile.TemporaryDirectory(prefix=f"muster-{pattern.id}-") as tmp:
        tmp_path = Path(tmp)
        _verify_units(pattern, tmp_path)
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        fake_systemd_analyze = fake_bin / "systemd-analyze"
        fake_systemd_analyze.write_text("#!/usr/bin/env sh\nexit 0\n")
        fake_systemd_analyze.chmod(0o755)
        env = os.environ.copy()
        env["MUSTER_MOCK_ROOT"] = tmp
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
        result = subprocess.run(
            [str(doctor)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=20,
        )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise PatternError(f"{doctor}: doctor failed for stable Tech 1 pattern: {output}")


def check_stable_tech1(patterns: list[Pattern]) -> None:
    for pattern in patterns:
        if pattern.tech_level != 1 or pattern.data["status"] != STABLE_STATUS:
            continue
        _check_no_scaffold_markers(pattern)
        _check_scripts_executable(pattern)
        _run_doctor(pattern)


def main() -> int:
    try:
        patterns = validate_all()
        check_stable_tech1(patterns)
    except PatternError as exc:
        print(f"stable Tech 1 check failed: {exc}")
        return 1
    count = sum(1 for pattern in patterns if pattern.tech_level == 1 and pattern.data["status"] == STABLE_STATUS)
    print(f"stable Tech 1 ok for {count} patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
