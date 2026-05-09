# Capability Mount

## Intent

Treat access to a resource such as NAS, secrets, cameras, or media as a capability with explicit ownership.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd. A capability check proves that a path is mounted or otherwise usable before a service writes to it. The default check treats an unmounted NAS destination as degraded rather than silently writing to local storage.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

A small set of systemd-facing artifacts plus scripts and examples document the operational boundary.

The capability owner is explicit: the unit that needs the resource calls `check-capability.sh` or depends on `muster-capability@.service` before starting destructive or high-volume work.

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

Run `scripts/install.sh` with no arguments first. It prints the copy plan. Use `--apply` only on the target host after reviewing capability names, paths, and credentials.

## Verification

Run `scripts/doctor.sh`, validate the repository, and then prove the service behavior on a disposable or mocked target before using real hardware.

The doctor runs the capability checker in mock mode and verifies that it records an explicit capability state.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Never commit credentials. Mount secrets through systemd credentials, protected files, or target-local setup.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
