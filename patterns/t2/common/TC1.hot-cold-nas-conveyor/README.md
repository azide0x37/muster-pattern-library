# Hot/Cold NAS Conveyor

## Intent

Keep hot local storage responsive while lazily moving cold output to NAS or other network storage.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd. Hot data lives under `/var/cache/muster/hot`; cold data is exposed at `/mnt/muster/cold` through the lazy mount pattern. `scripts/convey.sh` defaults to a mock root and uses real paths only with `--apply`.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

A small set of systemd-facing artifacts plus scripts and examples document the operational boundary.

## Subpatterns

- `C1.service-capsule`
- `C2.persistent-tick`
- `C4.lazy-resource-gate`
- `C5.failure-ratchet`

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` is a placeholder systemd artifact to adapt.
- `scripts/install.sh` documents the installation boundary.
- `scripts/doctor.sh` checks local pattern files.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Review the manifest, adapt the unit and scripts to the target host, then copy only the reviewed artifacts into the systemd-managed location for that machine.

Run `scripts/install.sh` first as a dry run. `--apply` installs the conveyor service, timer, and helper script, but does not enable the timer automatically.

## Verification

Run `scripts/doctor.sh`, validate the repository, and then prove the service behavior on a disposable or mocked target before using real hardware.

The doctor verifies unit files when systemd tooling exists and proves a mock hot-to-cold transfer in temporary storage.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
