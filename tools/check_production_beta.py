from __future__ import annotations

try:
    from completion import FLAGSHIP_CHAIN, PRODUCTION_BETA_STATUS, is_production_beta
    from patternlib import Pattern, PatternError, pattern_index, validate_all
except ModuleNotFoundError:
    from tools.completion import FLAGSHIP_CHAIN, PRODUCTION_BETA_STATUS, is_production_beta
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
    "TC1.hot-cold-nas-conveyor": {
        "units/muster-nas-conveyor.service",
        "units/muster-nas-conveyor.timer",
        "scripts/convey.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "TC3.scheduled-herald": {
        "units/muster-herald.service",
        "units/muster-herald.timer",
        "scripts/collect-status.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "TC4.self-healing-reconnector": {
        "units/muster-reconnect@.service",
        "units/muster-reconnect.timer",
        "scripts/reconnect.sh",
        "scripts/install.sh",
        "scripts/doctor.sh",
        "examples/minimal/README.md",
    },
    "TC5.local-sidecar-bridge": {
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


def check_production_beta(patterns: list[Pattern]) -> None:
    index = pattern_index(patterns)
    missing = sorted(FLAGSHIP_CHAIN - set(index))
    if missing:
        raise PatternError(f"missing flagship patterns: {', '.join(missing)}")

    for pattern in patterns:
        if is_production_beta(pattern) and pattern.id not in FLAGSHIP_CHAIN:
            raise PatternError(f"{pattern.path}: only flagship-chain patterns may claim production-beta status")

    for pattern_id in sorted(FLAGSHIP_CHAIN):
        pattern = index[pattern_id]
        if pattern.data["status"] != PRODUCTION_BETA_STATUS:
            raise PatternError(f"{pattern.path}: flagship pattern must be usable/reviewed/reviewed")
        required = REQUIRED_ARTIFACTS[pattern_id]
        actual = _artifact_paths(pattern)
        missing_artifacts = sorted(required - actual)
        if missing_artifacts:
            raise PatternError(f"{pattern.path}: missing production-beta artifacts: {', '.join(missing_artifacts)}")
        for relpath in required:
            if not (pattern.path.parent / relpath).exists():
                raise PatternError(f"{pattern.path}: required artifact does not exist: {relpath}")
        _fail_on_placeholders(pattern, required)


def main() -> int:
    try:
        patterns = validate_all()
        check_production_beta(patterns)
    except PatternError as exc:
        print(f"production-beta check failed: {exc}")
        return 1
    print(f"production-beta ok for {len(FLAGSHIP_CHAIN)} flagship patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
