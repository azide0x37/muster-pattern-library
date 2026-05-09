# Device Binding

## Intent

Attach service lifetime to the presence of a USB, serial, Bluetooth, camera, or other local device.

## Stable contract

Target platform is Debian/Raspberry Pi OS with systemd and udev. The udev rule must only request systemd work with `SYSTEMD_WANTS`; it must not perform long-running work directly. The template service receives a kernel device name and hands work to a bounded helper.

## When to use this

Use this when device presence should trigger or scope a systemd-owned service lifetime, especially for optical drives, USB serial adapters, cameras, and other local hardware.

## When not to use this

Do not use this when the device identity cannot be matched safely.

## System shape

The udev rule narrows the device match and asks systemd to start `muster-device-bound@%k.service`. The service binds to `dev-%i.device`, records an observation through `device-bound-run.sh`, and leaves status in `/run/muster/device-binding.json`.

The default example matches optical media devices (`sr[0-9]*`) because that is the narrowest future-DVD-ingester shape. Adapt the udev match before using it for USB serial, cameras, or other device classes.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `udev/90-muster-device-binding.rules` shows a udev-to-systemd handoff.
- `units/muster-device-bound@.service` binds service lifetime to the device.
- `scripts/device-bound-run.sh` records the bounded invocation.
- `scripts/install.sh`, `scripts/rollback.sh`, and `scripts/uninstall.sh` manage staged lifecycle artifacts.
- `scripts/doctor.sh` verifies the rule, unit, and mock invocation.

## Installation

Run `scripts/install.sh` without arguments to inspect the dry-run copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for staged verification, or `scripts/install.sh --apply` as root on a target host after reviewing the udev match.

## Verification

Run `scripts/doctor.sh`. The doctor verifies `SYSTEMD_WANTS`, rejects udev `RUN+=`, checks device binding in the unit, and runs the helper in mock mode.

## Failure modes

Bad udev matches can start the wrong unit. Missing systemd support means the rule cannot hand off work. Helper failures leave no long-running work inside udev; they surface as service failures and status files.

## Rollback

Run `scripts/rollback.sh --apply` to restore the previous installed unit, rule, and helper from the lifecycle ledger. Run `scripts/uninstall.sh --apply` to remove owned artifacts while preserving config and lifecycle records.

## Security notes

Prefer stable device attributes and avoid broad permissions on `/dev` paths.

## Future work

No known blocker for the stable contract. Future variants can add hardware-specific matching examples without changing the base lifecycle.
