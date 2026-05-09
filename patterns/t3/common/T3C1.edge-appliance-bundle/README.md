# Edge Appliance Bundle

## Intent

Turn a Raspberry Pi or similar host into a respectable local appliance with storage, status, recovery, and sidecar behavior.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd. The appliance contract uses `/etc/muster` for reviewed config, `/run/muster/status.json` for state, `/var/lib/muster` for durable local data, and `muster-recover@.service` as the manual recovery entrypoint. Network storage must never block boot.

## When to use this

Use this as the first real Muster target for a single-purpose edge appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

Local services, persistent jobs, lazy storage, health output, failure notification, and manual recovery entrypoints.

The health states are `healthy`, `degraded`, `failed`, and `unknown`. `unknown` is the safe default until Herald can prove a stronger state.

## Subpatterns

- `TC1.hot-cold-nas-conveyor`
- `TC3.scheduled-herald`
- `TC4.self-healing-reconnector`
- `TC5.local-sidecar-bridge`

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` is a placeholder systemd artifact to adapt.
- `scripts/install.sh` documents the installation boundary.
- `scripts/doctor.sh` checks local pattern files.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Review the manifest, adapt the unit and scripts to the target host, then copy only the reviewed artifacts into the systemd-managed location for that machine.

Run `scripts/install.sh` without arguments to inspect the appliance target, recovery unit, and helper copy plan. Use `--apply` only on the target host after dependency units have been reviewed.

## Verification

Run `scripts/doctor.sh`, validate the repository, and then prove the service behavior on a disposable or mocked target before using real hardware.

The doctor verifies the assembled target shape and runs the appliance probe against a temporary mock `/run/muster`.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
