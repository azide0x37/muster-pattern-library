# Capability Mount

## Intent

Treat access to a resource such as NAS, secrets, cameras, or media as a capability with explicit ownership.

## Stable contract

Target platform is Debian/Raspberry Pi OS with systemd. A capability check proves that a path is mounted or otherwise usable before a service writes to it. The default check treats an unmounted NAS destination as degraded rather than silently writing to local storage.

## When to use this

Use this when a service must prove access to a mount, credential-backed path, camera export, or media directory before doing destructive or high-volume work.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

The capability owner is explicit: the unit that needs the resource calls `check-capability.sh` or depends on `muster-capability@.service` before starting destructive or high-volume work.

The checker writes atomic status JSON under `/run/muster` and uses stable exit codes: `0` for healthy, `75` for degraded, and `1` for failed.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/muster-capability@.service` wraps the capability check.
- `scripts/check-capability.sh` verifies a named path and writes status JSON.
- `scripts/install.sh`, `scripts/rollback.sh`, and `scripts/uninstall.sh` manage staged lifecycle artifacts.
- `scripts/doctor.sh` verifies the unit and mock capability behavior.

## Installation

Run `scripts/install.sh` with no arguments first. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for staged verification, or `scripts/install.sh --apply` as root on a target host after reviewing capability names, paths, and credentials.

## Verification

Run `scripts/doctor.sh`. It runs the capability checker in mock mode and verifies explicit capability state output.

## Failure modes

Missing paths fail with exit `1`. Existing but unmounted apply-mode paths degrade with exit `75` when `findmnt` is available. Permission problems degrade with exit `75`. All outcomes write status JSON using a sanitized capability name.

## Rollback

Run `scripts/rollback.sh --apply` to restore the previous installed unit and helper. Run `scripts/uninstall.sh --apply` to remove owned artifacts while preserving config and lifecycle records.

## Security notes

Never commit credentials. Mount secrets through systemd credentials, protected files, or target-local setup.

## Future work

No known blocker for the stable contract. Future variants can add credential-specific examples without changing the base capability proof.
