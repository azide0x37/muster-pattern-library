# Lazy Resource Gate

## Intent

Materialize a mount or network resource only when touched so boot does not depend on flaky external infrastructure.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd. The cold-storage example uses a paired `.automount` and `.mount` for `/mnt/muster/cold`, includes `_netdev`, `nofail`, bounded timeout behavior, and does not make boot wait for NAS availability.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

A paired `.automount` and `.mount` defer the expensive or fragile resource until first access.

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

Run `scripts/install.sh` without arguments first. `--apply` copies only the reviewed mount and automount units. Credentials stay outside the repository at `/etc/muster/nas.credentials`.

## Verification

Run `scripts/doctor.sh`, validate the repository, and then prove the service behavior on a disposable or mocked target before using real hardware.

The doctor checks the mount artifacts and creates a mock cold-storage path to prove the local shape without mounting a real NAS.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
