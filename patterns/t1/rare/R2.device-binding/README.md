# Device Binding

## Intent

Attach service lifetime to the presence of a USB, serial, Bluetooth, camera, or other local device.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd and udev. The udev rule must only request systemd work with `SYSTEMD_WANTS`; it must not perform long-running work directly. The template service receives a kernel device name and hands work to a bounded helper.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when the device identity cannot be matched safely.

## System shape

A small set of systemd-facing artifacts plus scripts and examples document the operational boundary.

The default example matches optical media devices (`sr[0-9]*`) because that is the narrowest future-DVD-ingester shape. Adapt the udev match before using it for USB serial, cameras, or other device classes.

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

Run `scripts/install.sh` without arguments to inspect the dry-run copy plan. Use `--apply` only on the target host after reviewing the udev match.

## Verification

Run `scripts/doctor.sh`, validate the repository, and then prove the service behavior on a disposable or mocked target before using real hardware.

The doctor verifies the rule contains `SYSTEMD_WANTS`, checks the unit when systemd tooling is available, and runs the helper in mock mode.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Prefer stable device attributes and avoid broad permissions on `/dev` paths.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
