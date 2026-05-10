from __future__ import annotations

try:
    from completion import PRODUCTION_BETA_PATTERNS, PRODUCTION_BETA_STATUSES
    from patternlib import Pattern, PatternError, pattern_index, validate_all
except ModuleNotFoundError:
    from tools.completion import PRODUCTION_BETA_PATTERNS, PRODUCTION_BETA_STATUSES
    from tools.patternlib import Pattern, PatternError, pattern_index, validate_all


REQUIRED_ARTIFACTS = {
    "C1.service-capsule": {
        "units/example.service",
        "scripts/service-capsule-run.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "C2.persistent-tick": {
        "units/example.service",
        "units/example.timer",
        "scripts/persistent-tick-run.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "C4.lazy-resource-gate": {
        "units/mnt-muster-cold.automount",
        "units/mnt-muster-cold.mount",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "C5.failure-ratchet": {
        "units/example.service",
        "units/muster-recover@.service",
        "scripts/failure-prone-job.sh",
        "scripts/muster-recover.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "C6.lifecycle-capsule": {
        "units/example.service",
        "scripts/lifecycle-run.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "scripts/rollback.sh",
        "scripts/uninstall.sh",
        "examples/minimal/README.md",
    },
    "T2C1.hot-cold-nas-conveyor": {
        "units/muster-nas-conveyor.service",
        "units/muster-nas-conveyor.timer",
        "scripts/convey.sh",
        "scripts/wait-for-hot-capacity.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "T2C3.scheduled-herald": {
        "units/muster-herald.service",
        "units/muster-herald.timer",
        "scripts/collect-status.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "T2C4.self-healing-reconnector": {
        "units/muster-reconnect@.service",
        "units/muster-reconnect.timer",
        "scripts/reconnect.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "T2C5.local-sidecar-bridge": {
        "units/muster-sidecar-bridge.service",
        "units/muster-sidecar-bridge.timer",
        "scripts/bridge-status.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "T3C1.edge-appliance-bundle": {
        "units/muster-appliance.target",
        "units/muster-recover@.service",
        "scripts/appliance-doctor.sh",
        "scripts/muster-recover.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "R2.device-binding": {
        "udev/90-muster-device-binding.rules",
        "units/muster-device-bound@.service",
        "scripts/device-bound-run.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "scripts/rollback.sh",
        "scripts/uninstall.sh",
        "examples/minimal/README.md",
    },
    "R5.capability-mount": {
        "units/muster-capability@.service",
        "scripts/check-capability.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "scripts/rollback.sh",
        "scripts/uninstall.sh",
        "examples/minimal/README.md",
    },
    "T2R4.device-triggered-conveyor": {
        "udev/90-muster-device-conveyor.rules",
        "units/muster-device-conveyor@.service",
        "units/muster-device-conveyor-drain.service",
        "units/muster-device-conveyor-drain.timer",
        "scripts/device-convey.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "scripts/rollback.sh",
        "scripts/uninstall.sh",
        "examples/minimal/README.md",
    },
    "T2R5.signed-update-rail": {
        "units/muster-signed-update.service",
        "units/muster-signed-update.timer",
        "scripts/update.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "scripts/rollback.sh",
        "scripts/uninstall.sh",
        "examples/minimal/README.md",
    },
}


PLACEHOLDER_MARKERS = [
    "echo muster pattern",
    "placeholder",
]


def _artifact_paths(pattern: Pattern) -> set[str]:
    paths: set[str] = set()
    for values in pattern.data["artifacts"].values():
        paths.update(values)
    return paths


def _fail_on_placeholders(pattern: Pattern, relpaths: set[str]) -> None:
    for relpath in relpaths:
        path = pattern.path.parent / relpath
        if not path.exists() or path.is_dir():
            continue
        text = path.read_text(errors="ignore").lower()
        for marker in PLACEHOLDER_MARKERS:
            if marker in text:
                raise PatternError(f"{path}: production-beta artifact contains marker {marker!r}")


def _check_lifecycle_metadata(pattern: Pattern) -> None:
    lifecycle = pattern.data.get("lifecycle")
    if not isinstance(lifecycle, dict):
        raise PatternError(f"{pattern.path}: production-beta pattern must declare lifecycle metadata")
    install_modes = set(lifecycle["install_modes"])
    doctor_modes = set(lifecycle["doctor_modes"])
    if not ({"dry_run", "staged_root"} & install_modes):
        raise PatternError(f"{pattern.path}: lifecycle.install_modes must include dry_run or staged_root")
    if not ({"mock", "staged_root"} & doctor_modes):
        raise PatternError(f"{pattern.path}: lifecycle.doctor_modes must include mock or staged_root")

    actual = _artifact_paths(pattern)
    if lifecycle["managed"]:
        required = {"scripts/rollback.sh", "scripts/uninstall.sh"}
        missing = sorted(required - actual)
        if missing:
            raise PatternError(f"{pattern.path}: managed lifecycle is missing artifacts: {', '.join(missing)}")
        if lifecycle["uninstall"] != "artifacts_only":
            raise PatternError(f"{pattern.path}: managed lifecycle must use artifact-only uninstall by default")
    if lifecycle["update"] != "none" and "scripts/update.sh" not in actual:
        raise PatternError(f"{pattern.path}: update lifecycle must declare scripts/update.sh")


def check_production_beta(patterns: list[Pattern]) -> None:
    index = pattern_index(patterns)
    missing = sorted(PRODUCTION_BETA_PATTERNS - set(index))
    if missing:
        raise PatternError(f"missing production-beta patterns: {', '.join(missing)}")

    for pattern_id in sorted(PRODUCTION_BETA_PATTERNS):
        pattern = index[pattern_id]
        if pattern.data["status"] not in PRODUCTION_BETA_STATUSES:
            raise PatternError(f"{pattern.path}: production-beta pattern must be usable/reviewed/reviewed or stable/stable/stable")
        required = REQUIRED_ARTIFACTS[pattern_id]
        actual = _artifact_paths(pattern)
        missing_artifacts = sorted(required - actual)
        if missing_artifacts:
            raise PatternError(f"{pattern.path}: missing production-beta artifacts: {', '.join(missing_artifacts)}")
        for relpath in required:
            if not (pattern.path.parent / relpath).exists():
                raise PatternError(f"{pattern.path}: required artifact does not exist: {relpath}")
        _check_lifecycle_metadata(pattern)
        _fail_on_placeholders(pattern, required)


def main() -> int:
    try:
        patterns = validate_all()
        check_production_beta(patterns)
    except PatternError as exc:
        print(f"production-beta check failed: {exc}")
        return 1
    print(f"production-beta ok for {len(PRODUCTION_BETA_PATTERNS)} patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
