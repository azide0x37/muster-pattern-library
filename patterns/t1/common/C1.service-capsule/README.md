# Service Capsule

## Intent

Run one well-bounded daemon or script as a managed service with explicit environment, user, restart, and logging behavior.

## When to use this

Use this for any daemon or long-running script that deserves a clear unit boundary.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

One `.service` file, one environment file convention, a restricted runtime user, and a small doctor script.

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

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
