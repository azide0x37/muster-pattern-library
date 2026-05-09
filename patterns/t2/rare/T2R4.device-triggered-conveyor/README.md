# Device-Triggered Conveyor

## Intent

Bind a physical device event to a bounded ingest job that waits for hot-storage capacity, proves cold-storage capability, stages local work, and hands output to a hot/cold conveyor.

## Stable contract

Target platform is Debian/Raspberry Pi OS with systemd and udev. udev only requests `muster-device-conveyor@%k.service`; systemd owns the job lifecycle. The job must prove the cold-storage capability before it starts high-volume work and must wait for hot-storage capacity instead of failing immediately when the conveyor is still flushing.

## When to use this

Use this for optical drives, cameras, USB capture devices, or similar resources where insertion/presence should trigger one bounded ingest job.

## When not to use this

Do not use this when a watched folder is the natural boundary; use `T2C2.dropfolder-spooler` for file arrival workflows. Do not use it when the device event itself must run long work inside udev.

## System shape

`udev/90-muster-device-conveyor.rules` matches the device and asks systemd to start `muster-device-conveyor@%k.service`. `scripts/device-convey.sh` then:

- records the device event
- proves the destination capability
- waits for hot-storage capacity
- claims a per-device run directory
- writes a mock payload or runs an ingest command
- marks complete/failed state
- leaves output for the hot/cold conveyor

The drain timer exists so queued or partial work can continue moving cold even when no new device event arrives.

## Subpatterns

- `C1.service-capsule`
- `C2.persistent-tick`
- `C4.lazy-resource-gate`
- `C5.failure-ratchet`
- `R2.device-binding`
- `R5.capability-mount`
- `T2C1.hot-cold-nas-conveyor`
- `T2C3.scheduled-herald`

## Files

- `manifest.yaml` declares the pattern contract.
- `udev/90-muster-device-conveyor.rules` shows the udev-to-systemd trigger.
- `units/muster-device-conveyor@.service` runs one ingest job.
- `units/muster-device-conveyor-drain.*` keeps cold publishing moving.
- `scripts/device-convey.sh` implements mockable device ingest with capacity waiting.
- `scripts/install.sh`, `scripts/rollback.sh`, and `scripts/uninstall.sh` manage staged lifecycle artifacts.
- `scripts/doctor.sh` provides mock verification.

## Installation

Run `scripts/install.sh` without arguments first. It prints the systemd, udev, and helper copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for staged verification, or `scripts/install.sh --apply` as root after reviewing device matches, capability paths, and ingest command. The install copies `device-convey.sh`, `convey`, and `wait-for-hot-capacity.sh`.

## Verification

Run `scripts/doctor.sh`. It checks udev and unit shape, then simulates the important backpressure case: a device arrives while hot storage is full, a drain command frees capacity, and ingest continues.

## Failure modes

If capability proof fails, the job exits before high-volume work. If hot capacity never appears before timeout, the job records `capacity_timeout` and exits as temporary failure. If ingest fails after claiming a run directory, `.ingest-failed` remains for inspection.

## Rollback

Run `scripts/rollback.sh --apply` to restore the previous installed units, udev rule, and helpers. Run `scripts/uninstall.sh --apply` to remove owned artifacts while preserving config, state, and lifecycle records.

## Security notes

Treat the udev rule and ingest command as privileged-code boundaries. Keep device matches narrow. Do not allow the destination capability check to degrade into writing to an unmounted local directory.

## Future work

No known blocker for the stable contract. Future variants can add library-specific probes and richer metadata extraction without changing the base conveyor lifecycle.
