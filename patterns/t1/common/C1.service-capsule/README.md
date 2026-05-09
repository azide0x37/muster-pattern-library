# Service Capsule

## Intent

Run one well-bounded daemon or script as a managed service with explicit environment, user, restart, and logging behavior.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd. The example service runs as `muster`, reads `/etc/muster/service-capsule.env`, writes only under `/run/muster` and `/var/lib/muster`, and uses `Restart=on-failure` with a bounded restart delay. `scripts/service-capsule-run.sh` defaults to mock mode and writes a health fact before the unit is installed with `--apply`.

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

Run `scripts/install.sh` first with no arguments. It prints the intended copies. Use `scripts/install.sh --apply` only on the target host after creating the `muster` user and reviewing the unit paths.

## Verification

Run `scripts/doctor.sh`, validate the repository, and then prove the service behavior on a disposable or mocked target before using real hardware.

The doctor checks local files, verifies the unit with `systemd-analyze` when available, and exercises the workload script against a temporary mock root.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
