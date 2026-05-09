# Failure Ratchet

## Intent

Turn service failure into a first-class event that can log, notify, quarantine, retry, or degrade deliberately.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd. The example job uses `OnFailure=muster-recover@%n.service`, while the recovery handler records a degraded state under `/run/muster`. Both helper scripts default to mock mode and require `--apply` for real runtime paths.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

A unit uses `OnFailure=` to trigger a recovery or notification service with enough context to act.

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

Run `scripts/install.sh` without arguments to inspect the unit and helper copy plan. Use `--apply` only after deciding how the target host should notify operators.

## Verification

Run `scripts/doctor.sh`, validate the repository, and then prove the service behavior on a disposable or mocked target before using real hardware.

The doctor validates the recovery unit shape and runs both the protected job and recovery script against a temporary mock root.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
