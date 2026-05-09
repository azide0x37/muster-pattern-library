from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import argparse
import textwrap


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class PatternSpec:
    id: str
    name: str
    tech_level: int
    rarity: str
    mrl: int
    summary: str
    provides: list[str]
    requires: list[str]
    subpatterns: list[str] = field(default_factory=list)
    composes_with: list[str] = field(default_factory=list)
    use: str = "Use this when the capability needs to be repeatable across a small Linux appliance."
    avoid: str = "Do not use this when a one-off shell command is clearer than a managed operational contract."
    shape: str = "A small set of systemd-facing artifacts plus scripts and examples document the operational boundary."
    failure: str = "Expected failures should leave inspectable logs, status files, or failed artifacts."
    security: str = "Review users, paths, credentials, sockets, and device permissions before deploying."
    future: str = "Replace placeholders with hardware-specific checks and add integration tests as the pattern matures."

    @property
    def slug(self) -> str:
        return self.id.split(".", 1)[1]

    @property
    def folder(self) -> Path:
        return ROOT / "patterns" / f"t{self.tech_level}" / self.rarity / self.id


PATTERNS = [
    PatternSpec(
        "C1.service-capsule",
        "Service Capsule",
        1,
        "common",
        9,
        "Run one well-bounded daemon or script as a managed service with explicit environment, user, restart, and logging behavior.",
        ["managed_process"],
        ["systemd.service"],
        composes_with=["C2.persistent-tick", "C5.failure-ratchet"],
        use="Use this for any daemon or long-running script that deserves a clear unit boundary.",
        shape="One `.service` file, one environment file convention, a restricted runtime user, and a small doctor script.",
    ),
    PatternSpec(
        "C2.persistent-tick",
        "Persistent Tick",
        1,
        "common",
        9,
        "Run recurring jobs with a timer that catches up after downtime and reports failure through a bounded oneshot service.",
        ["recurring_job", "downtime_catchup"],
        ["systemd.timer", "systemd.service"],
        composes_with=["C1.service-capsule", "C5.failure-ratchet"],
        shape="A `.timer` with `Persistent=true` activates a oneshot `.service` that performs the work.",
    ),
    PatternSpec(
        "C3.dropfolder-trigger",
        "Dropfolder Trigger",
        1,
        "common",
        8,
        "React to files appearing in a watched folder and hand them to a safe processing service.",
        ["filesystem_event_processing"],
        ["systemd.path", "systemd.service"],
        composes_with=["C1.service-capsule", "C5.failure-ratchet"],
        shape="A `.path` unit watches an inbox and starts a oneshot processor service.",
    ),
    PatternSpec(
        "C4.lazy-resource-gate",
        "Lazy Resource Gate",
        1,
        "common",
        8,
        "Materialize a mount or network resource only when touched so boot does not depend on flaky external infrastructure.",
        ["lazy_resource", "boot_safe_mount"],
        ["systemd.automount", "systemd.mount"],
        composes_with=["C5.failure-ratchet"],
        shape="A paired `.automount` and `.mount` defer the expensive or fragile resource until first access.",
    ),
    PatternSpec(
        "C5.failure-ratchet",
        "Failure Ratchet",
        1,
        "common",
        7,
        "Turn service failure into a first-class event that can log, notify, quarantine, retry, or degrade deliberately.",
        ["failure_event", "recovery_entrypoint"],
        ["systemd.service"],
        composes_with=["C1.service-capsule", "C2.persistent-tick"],
        shape="A unit uses `OnFailure=` to trigger a recovery or notification service with enough context to act.",
    ),
    PatternSpec(
        "R1.socket-anteroom",
        "Socket Anteroom",
        1,
        "rare",
        7,
        "Expose a local API or control endpoint through socket activation without keeping the backing service hot.",
        ["socket_activated_control_plane"],
        ["systemd.socket", "systemd.service"],
        composes_with=["C1.service-capsule"],
        avoid="Do not use this for public network surfaces until authentication and binding are explicit.",
        security="Bind to localhost by default and treat every socket as an API surface.",
    ),
    PatternSpec(
        "R2.device-binding",
        "Device Binding",
        1,
        "rare",
        6,
        "Attach service lifetime to the presence of a USB, serial, Bluetooth, camera, or other local device.",
        ["device_scoped_lifetime"],
        ["udev", "systemd.device", "systemd.service"],
        composes_with=["C1.service-capsule", "C5.failure-ratchet"],
        avoid="Do not use this when the device identity cannot be matched safely.",
        security="Prefer stable device attributes and avoid broad permissions on `/dev` paths.",
    ),
    PatternSpec(
        "R3.cgroup-governor",
        "Cgroup Governor",
        1,
        "rare",
        6,
        "Constrain CPU, memory, IO, and restart behavior so one bad citizen cannot take down a small appliance.",
        ["resource_governance"],
        ["systemd.service", "cgroups"],
        composes_with=["C1.service-capsule"],
        shape="Resource control directives sit next to restart policy and operator-facing limits.",
    ),
    PatternSpec(
        "R4.state-ledger",
        "State Ledger",
        1,
        "rare",
        6,
        "Make services explain themselves through journald and small runtime JSON facts under `/run/muster`.",
        ["runtime_facts", "operator_status"],
        ["journald", "runtime_directory"],
        composes_with=["T2C3.scheduled-herald"],
        shape="Services write concise facts with boot/session IDs, timestamps, and confidence values.",
    ),
    PatternSpec(
        "R5.capability-mount",
        "Capability Mount",
        1,
        "rare",
        5,
        "Treat access to a resource such as NAS, secrets, cameras, or media as a capability with explicit ownership.",
        ["resource_capability"],
        ["systemd.mount", "credentials"],
        composes_with=["C4.lazy-resource-gate", "C5.failure-ratchet"],
        security="Never commit credentials. Mount secrets through systemd credentials, protected files, or target-local setup.",
    ),
    PatternSpec(
        "M1.local-truth-sheaf",
        "Local Truth Sheaf",
        1,
        "mythic",
        4,
        "Have each unit report local truth and use a reducer to decide whether those facts glue into coherent machine state.",
        ["local_truth", "state_reducer"],
        ["runtime_facts"],
        [],
        use="Use this as a small status reducer before attempting any logic-heavy orchestration.",
        avoid="Do not use this to hide uncertainty behind a single fake health boolean.",
        future="Graduate toward Rare by standardizing fact schemas and proving real appliances can share them.",
    ),
    PatternSpec(
        "M2.holonomy-detector",
        "Holonomy Detector",
        1,
        "mythic",
        4,
        "Run a loop through expected states and detect whether the system actually returns to identity.",
        ["drift_detection", "loop_probe"],
        ["runtime_facts"],
        [],
        failure="Failed loops indicate leaked mounts, stuck devices, ghost processes, or inconsistent state.",
    ),
    PatternSpec(
        "M3.simplicial-task-graph",
        "Simplicial Task Graph",
        1,
        "mythic",
        3,
        "Model target states as filled dependency shapes where missing faces explain why the desired state cannot exist.",
        ["explainable_dependency_state"],
        ["dependency_model"],
        [],
        avoid="Do not use this where ordinary target dependencies and health checks explain enough.",
    ),
    PatternSpec(
        "M4.local-topos-runtime",
        "Local Topos Runtime",
        1,
        "mythic",
        2,
        "Treat targets as propositions, services as proofs, and observed paths or devices as evidence for valid local state.",
        ["operational_logic"],
        ["state_model"],
        [],
        security="Keep any actuator behind explicit policy; logic engines should not gain ambient authority.",
    ),
    PatternSpec(
        "M5.temporal-sheaf",
        "Temporal Sheaf",
        1,
        "mythic",
        3,
        "Glue persistent timers, snapshots, and boot/session facts so machines remember obligations across downtime.",
        ["temporal_state", "downtime_memory"],
        ["persistent_timers", "runtime_snapshots"],
        [],
        use="Use this where a machine sleeps, reboots, or roams but still owes work after returning.",
    ),
    PatternSpec(
        "T2C1.hot-cold-nas-conveyor",
        "Hot/Cold NAS Conveyor",
        2,
        "common",
        8,
        "Keep hot local storage responsive while lazily moving cold output to NAS or other network storage.",
        ["hot_cold_storage_flow"],
        ["C1.service-capsule", "C2.persistent-tick", "C4.lazy-resource-gate", "C5.failure-ratchet"],
        ["C1.service-capsule", "C2.persistent-tick", "C4.lazy-resource-gate", "C5.failure-ratchet"],
        ["T3C1.edge-appliance-bundle"],
    ),
    PatternSpec(
        "T2C2.dropfolder-spooler",
        "Dropfolder Spooler",
        2,
        "common",
        8,
        "Claim, process, and sort inbound files from a watched folder into done, failed, and log locations.",
        ["spooler_lifecycle"],
        ["C1.service-capsule", "C3.dropfolder-trigger", "C5.failure-ratchet"],
        ["C1.service-capsule", "C3.dropfolder-trigger", "C5.failure-ratchet"],
        ["T2R3.edge-control-plane"],
    ),
    PatternSpec(
        "T2C3.scheduled-herald",
        "Scheduled Herald",
        2,
        "common",
        8,
        "Periodically collect machine status and publish it as a runtime file, MOTD source, API payload, or notification.",
        ["scheduled_status_report"],
        ["C1.service-capsule", "C2.persistent-tick", "C5.failure-ratchet"],
        ["C1.service-capsule", "C2.persistent-tick", "C5.failure-ratchet"],
        ["T3C1.edge-appliance-bundle"],
    ),
    PatternSpec(
        "T2C4.self-healing-reconnector",
        "Self-Healing Reconnector",
        2,
        "common",
        7,
        "Use a watcher and timer fallback to reconnect flaky resources without rebooting the whole machine.",
        ["bounded_reconnect_loop"],
        ["C1.service-capsule", "C2.persistent-tick", "C5.failure-ratchet"],
        ["C1.service-capsule", "C2.persistent-tick", "C5.failure-ratchet"],
        ["T2R1.bluetooth-audio-gateway", "T3C1.edge-appliance-bundle"],
    ),
    PatternSpec(
        "T2C5.local-sidecar-bridge",
        "Local Sidecar Bridge",
        2,
        "common",
        7,
        "Poll or normalize a local subsystem and publish clean state outward through MQTT, HTTP, files, or another bridge.",
        ["local_state_bridge"],
        ["C1.service-capsule", "C2.persistent-tick", "C5.failure-ratchet"],
        ["C1.service-capsule", "C2.persistent-tick", "C5.failure-ratchet"],
        ["T2R1.bluetooth-audio-gateway", "T2R3.edge-control-plane"],
    ),
    PatternSpec(
        "T2R1.bluetooth-audio-gateway",
        "Bluetooth Audio Gateway",
        2,
        "rare",
        6,
        "Monitor a specific Bluetooth speaker, reconnect it, route audio, and expose honest state to a local control plane.",
        ["bluetooth_audio_path", "audio_gateway_status"],
        ["T2C4.self-healing-reconnector", "T2C5.local-sidecar-bridge", "R2.device-binding", "R4.state-ledger"],
        ["T2C4.self-healing-reconnector", "T2C5.local-sidecar-bridge", "R2.device-binding", "R4.state-ledger"],
        ["T3R1.multi-resource-orchestrator"],
        avoid="Do not pretend Bluetooth connected, routed, and playable are the same state.",
        failure="Failures include device absent, connected without sink, routed without playback, and state stale.",
    ),
    PatternSpec(
        "T2R2.lazy-capability-media-bus",
        "Lazy Capability Media Bus",
        2,
        "rare",
        5,
        "Expose media or storage through a lazy resource, cgroup limits, and an API anteroom that materializes capabilities on demand.",
        ["lazy_media_capability"],
        ["T2C1.hot-cold-nas-conveyor", "R1.socket-anteroom", "R3.cgroup-governor", "R5.capability-mount"],
        ["T2C1.hot-cold-nas-conveyor", "R1.socket-anteroom", "R3.cgroup-governor", "R5.capability-mount"],
        ["T3R1.multi-resource-orchestrator"],
    ),
    PatternSpec(
        "T2R3.edge-control-plane",
        "Edge Control Plane",
        2,
        "rare",
        5,
        "Combine watched jobs, device binding, socket activation, status ledgers, and outward state publishing for a Pi-local machine plane.",
        ["edge_control_plane"],
        ["T2C2.dropfolder-spooler", "T2C3.scheduled-herald", "T2C5.local-sidecar-bridge", "R1.socket-anteroom", "R2.device-binding", "R4.state-ledger"],
        ["T2C2.dropfolder-spooler", "T2C3.scheduled-herald", "T2C5.local-sidecar-bridge", "R1.socket-anteroom", "R2.device-binding", "R4.state-ledger"],
        ["T3R1.multi-resource-orchestrator"],
    ),
    PatternSpec(
        "T3C1.edge-appliance-bundle",
        "Edge Appliance Bundle",
        3,
        "common",
        7,
        "Turn a Raspberry Pi or similar host into a respectable local appliance with storage, status, recovery, and sidecar behavior.",
        ["local_appliance", "health_report", "recoverable_runtime"],
        ["T2C1.hot-cold-nas-conveyor", "T2C3.scheduled-herald", "T2C4.self-healing-reconnector", "T2C5.local-sidecar-bridge"],
        ["T2C1.hot-cold-nas-conveyor", "T2C3.scheduled-herald", "T2C4.self-healing-reconnector", "T2C5.local-sidecar-bridge"],
        ["T3R1.multi-resource-orchestrator", "T3M1.machine-priest"],
        use="Use this as the first real Muster target for a single-purpose edge appliance.",
        shape="Local services, persistent jobs, lazy storage, health output, failure notification, and manual recovery entrypoints.",
    ),
    PatternSpec(
        "T3R1.multi-resource-orchestrator",
        "Multi-Resource Orchestrator",
        3,
        "rare",
        5,
        "Manage several flaky physical resources as one composed appliance with explicit ownership, degradation, and partial restart policy.",
        ["resource_ownership", "degraded_state_model"],
        ["T3C1.edge-appliance-bundle", "T2R1.bluetooth-audio-gateway", "T2R2.lazy-capability-media-bus", "T2R3.edge-control-plane", "R2.device-binding", "R4.state-ledger"],
        ["T3C1.edge-appliance-bundle", "T2R1.bluetooth-audio-gateway", "T2R2.lazy-capability-media-bus", "T2R3.edge-control-plane", "R2.device-binding", "R4.state-ledger"],
        ["T3M1.machine-priest"],
        failure="Failures should degrade one owned resource at a time rather than rebooting the full host.",
    ),
    PatternSpec(
        "T3M1.machine-priest",
        "Machine Priest",
        3,
        "mythic",
        3,
        "Interpret local operational facts into a canonical truth document that can explain healthy, degraded, unsafe, or unknown state.",
        ["canonical_machine_truth", "recommended_action"],
        ["T3C1.edge-appliance-bundle", "T3R1.multi-resource-orchestrator", "M1.local-truth-sheaf", "M5.temporal-sheaf"],
        ["T3C1.edge-appliance-bundle", "T3R1.multi-resource-orchestrator", "M1.local-truth-sheaf", "M5.temporal-sheaf"],
        [],
        use="Use the minimum version as a Python status reducer over `systemctl show`, `/run/muster/*.json`, mounts, and probes.",
        avoid="Do not allow narrative status to become an unchecked recovery actuator.",
    ),
    PatternSpec(
        "T3M2.ritualized-recovery-loop",
        "Ritualized Recovery Loop",
        3,
        "mythic",
        4,
        "Turn recovery into a staged sequence: observe, isolate, reset, rebind, validate, and rejoin.",
        ["staged_recovery"],
        ["C5.failure-ratchet", "T2C4.self-healing-reconnector", "R4.state-ledger", "M2.holonomy-detector", "M5.temporal-sheaf"],
        ["C5.failure-ratchet", "T2C4.self-healing-reconnector", "R4.state-ledger", "M2.holonomy-detector", "M5.temporal-sheaf"],
        [],
        use="Build this first for resources that are already expensive to recover manually.",
    ),
    PatternSpec(
        "T3M3.sheaf-of-services",
        "Sheaf of Services",
        3,
        "mythic",
        2,
        "Have services report local facts and let a gluing layer decide whether they form a coherent global machine state.",
        ["global_state_gluing"],
        ["M1.local-truth-sheaf", "M3.simplicial-task-graph", "T2R3.edge-control-plane", "T2C3.scheduled-herald"],
        ["M1.local-truth-sheaf", "M3.simplicial-task-graph", "T2R3.edge-control-plane", "T2C3.scheduled-herald"],
        [],
    ),
    PatternSpec(
        "T3M4.holonomic-watchdog",
        "Holonomic Watchdog",
        3,
        "mythic",
        3,
        "Periodically walk a loop through expected states and detect whether the machine returns to identity.",
        ["watchdog_drift_loop"],
        ["M2.holonomy-detector", "T2C3.scheduled-herald", "T2C4.self-healing-reconnector", "R4.state-ledger"],
        ["M2.holonomy-detector", "T2C3.scheduled-herald", "T2C4.self-healing-reconnector", "R4.state-ledger"],
        [],
    ),
    PatternSpec(
        "T3M5.intent-bound-runtime",
        "Intent-Bound Runtime",
        3,
        "mythic",
        2,
        "Declare desired operational intent and let a disciplined runtime choose the service graph that satisfies it.",
        ["intent_to_runtime_graph"],
        ["M4.local-topos-runtime", "M5.temporal-sheaf", "T2R3.edge-control-plane", "R5.capability-mount"],
        ["M4.local-topos-runtime", "M5.temporal-sheaf", "T2R3.edge-control-plane", "R5.capability-mount"],
        [],
        avoid="Do not use this until the plain service graph is already reliable and observable.",
        security="Intent runtimes must have strict policy boundaries around any action that changes machine state.",
    ),
]


EXAMPLES = {
    "edge-appliance-bundle": {
        "title": "Edge Appliance Bundle",
        "patterns": ["T3C1.edge-appliance-bundle", "T2C1.hot-cold-nas-conveyor", "T2C3.scheduled-herald", "T2C4.self-healing-reconnector", "T2C5.local-sidecar-bridge"],
        "body": "A baseline Pi-style appliance with local service management, lazy storage, scheduled status, bounded recovery, and outward state publishing.",
    },
    "bluetooth-audio-gateway": {
        "title": "Bluetooth Audio Gateway",
        "patterns": ["T2R1.bluetooth-audio-gateway", "T3R1.multi-resource-orchestrator", "R2.device-binding", "R4.state-ledger"],
        "body": "A Bluetooth audio appliance that distinguishes device visibility, connection, sink routing, playback, and Home Assistant visibility.",
    },
    "dvd-ripper-pi": {
        "title": "DVD Ripper Pi",
        "patterns": ["C1.service-capsule", "C2.persistent-tick", "C3.dropfolder-trigger", "C4.lazy-resource-gate", "C5.failure-ratchet", "T2C1.hot-cold-nas-conveyor", "T2C2.dropfolder-spooler", "T2C3.scheduled-herald", "T3C1.edge-appliance-bundle"],
        "body": "A user-owned-media workflow sketch that keeps commands as placeholders, sends output through hot/cold storage, and reports status through Herald.",
    },
    "gcode-spooler": {
        "title": "G-code Spooler",
        "patterns": ["T2C2.dropfolder-spooler", "T2R3.edge-control-plane", "R2.device-binding"],
        "body": "A safe mock-first spooler with inbox claiming, done/failed folders, fake sender behavior, serial binding stubs, and safety interlock placeholders.",
    },
}


def yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "\n" + "\n".join(f"  - {value}" for value in values)


def render_manifest(spec: PatternSpec) -> str:
    return f"""id: {spec.id}
name: {spec.name}
tech_level: {spec.tech_level}
rarity: {spec.rarity}
mrl: {spec.mrl}
summary: >
  {spec.summary}
provides:{yaml_list(spec.provides)}
requires:{yaml_list(spec.requires)}
subpatterns:{yaml_list(spec.subpatterns)}
composes_with:{yaml_list(spec.composes_with)}
lifecycle:
  managed: false
  install_modes:
    - dry_run
  doctor_modes:
    - mock
  rollback: documented
  uninstall: documented
  update: none
artifacts:
  units:
    - units/example.service
  scripts:
    - scripts/install.sh
    - scripts/doctor.sh
  tests:
    - tests/test_manifest.py
  examples:
    - examples/minimal/README.md
status:
  implementation: draft
  docs: draft
  tests: draft
"""


def render_readme(spec: PatternSpec) -> str:
    subpatterns = "\n".join(f"- `{item}`" for item in spec.subpatterns) or "None."
    return f"""# {spec.name}

## Intent

{spec.summary}

## When to use this

{spec.use}

## When not to use this

{spec.avoid}

## System shape

{spec.shape}

## Subpatterns

{subpatterns}

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` is a placeholder systemd artifact to adapt.
- `scripts/install.sh` documents the installation boundary.
- `scripts/doctor.sh` checks local pattern files.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Review the manifest, adapt the unit and scripts to the target host, then copy only the reviewed artifacts into the systemd-managed location for that machine.

## Verification

Run `scripts/doctor.sh`, validate the repository, and then prove the service behavior on a disposable or mocked target before using real hardware.

## Failure modes

{spec.failure}

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

{spec.security}

## Future work

{spec.future}
"""


def render_unit(spec: PatternSpec) -> str:
    return f"""[Unit]
Description=Muster example for {spec.name}
Documentation=file:README.md

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo muster pattern {spec.id}'
"""


def render_install(spec: PatternSpec) -> str:
    return f"""#!/usr/bin/env sh
set -eu

printf '%s\\n' "Pattern {spec.id}: review units and scripts before installing on a target host."
"""


def render_doctor(spec: PatternSpec) -> str:
    return f"""#!/usr/bin/env sh
set -eu

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/example.service"
printf '%s\\n' "ok: {spec.id}"
"""


def render_pattern_test() -> str:
    return """from pathlib import Path


def test_manifest_and_readme_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "manifest.yaml").exists()
    assert (root / "README.md").exists()
"""


def render_minimal_example(spec: PatternSpec) -> str:
    return f"""# Minimal {spec.name}

This sketch shows the smallest local artifact set for `{spec.id}`.

Start with the manifest, adapt `units/example.service`, and keep the first deployment mocked until `scripts/doctor.sh` and repository validation pass.
"""


def render_example_readme(slug: str, data: dict[str, object]) -> str:
    pattern_lines = "\n".join(f"- `{item}`" for item in data["patterns"])  # type: ignore[index]
    return f"""# {data["title"]}

{data["body"]}

## Pattern Map

{pattern_lines}

## Architecture

```text
operator input -> local queue/control plane -> managed services -> status ledger -> outward report
```

## Mock Mode

Keep the first pass mocked. Replace hardware commands with `printf`, local files, and fake status payloads until the lifecycle is visible.

## Success Criteria

- The example maps every moving part to a Muster pattern ID.
- Failure leaves inspectable files or status.
- Real hardware actuation is absent by default.
"""


def write(path: Path, content: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise SystemExit(f"{path} exists; rerun with --force to overwrite generated scaffold")
    path.write_text(textwrap.dedent(content).lstrip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    for spec in PATTERNS:
        folder = spec.folder
        write(folder / "manifest.yaml", render_manifest(spec), args.force)
        write(folder / "README.md", render_readme(spec), args.force)
        write(folder / "units" / "example.service", render_unit(spec), args.force)
        write(folder / "scripts" / "install.sh", render_install(spec), args.force)
        write(folder / "scripts" / "doctor.sh", render_doctor(spec), args.force)
        write(folder / "tests" / "test_manifest.py", render_pattern_test(), args.force)
        write(folder / "examples" / "minimal" / "README.md", render_minimal_example(spec), args.force)

    for slug, data in EXAMPLES.items():
        write(ROOT / "examples" / slug / "README.md", render_example_readme(slug, data), args.force)

    print(f"scaffolded {len(PATTERNS)} patterns and {len(EXAMPLES)} examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
