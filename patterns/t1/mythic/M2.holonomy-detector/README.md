# Holonomy Detector

## Intent

Run a loop through expected states and detect whether the system actually returns to identity.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

A small set of systemd-facing artifacts plus scripts and examples document the operational boundary.

## Subpatterns

None.

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

Failed loops indicate leaked mounts, stuck devices, ghost processes, or inconsistent state.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
