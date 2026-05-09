# Socket Anteroom

## Intent

Expose a local API or control endpoint through socket activation without keeping the backing service hot.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this for public network surfaces until authentication and binding are explicit.

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

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Bind to localhost by default and treat every socket as an API surface.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
