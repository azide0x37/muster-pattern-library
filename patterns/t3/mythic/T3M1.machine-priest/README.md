# Machine Priest

## Intent

Interpret local operational facts into a canonical truth document that can explain healthy, degraded, unsafe, or unknown state.

## When to use this

Use the minimum version as a Python status reducer over `systemctl show`, `/run/muster/*.json`, mounts, and probes.

## When not to use this

Do not allow narrative status to become an unchecked recovery actuator.

## System shape

A small set of systemd-facing artifacts plus scripts and examples document the operational boundary.

## Subpatterns

- `T3C1.edge-appliance-bundle`
- `T3R1.multi-resource-orchestrator`
- `M1.local-truth-sheaf`
- `M5.temporal-sheaf`

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

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
