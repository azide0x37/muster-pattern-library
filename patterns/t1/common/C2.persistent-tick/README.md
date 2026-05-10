# Persistent Tick

## Intent

Run recurring jobs with a timer that catches up after downtime and reports failure through a bounded oneshot service.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd. The timer uses `Persistent=true`, a randomized delay, and a oneshot service that runs as `muster`. `scripts/persistent-tick-run.sh` writes a timestamped runtime fact in mock mode by default and under `/run/muster` only when invoked with `--apply`.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

A `.timer` with `Persistent=true` activates a oneshot `.service` that performs the work.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` is a reviewed oneshot service artifact.
- `scripts/install.sh` documents the installation boundary.
- `scripts/doctor.sh` checks local pattern files.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Review the manifest, adapt the unit and scripts to the target host, then copy only the reviewed artifacts into the systemd-managed location for that machine.

Run `scripts/install.sh` without arguments to inspect the copy plan. `--apply` copies the service, timer, and helper script to system locations.

## Verification

Run `scripts/doctor.sh`, validate the repository, and then prove the service behavior on a disposable or mocked target before using real hardware.

The doctor checks the service/timer pair and exercises one mock tick without touching systemd state.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

No known blocker for the stable contract. Future variants can add job-specific backoff, reporting, or calendar policy without changing the base persistent timer shape.
