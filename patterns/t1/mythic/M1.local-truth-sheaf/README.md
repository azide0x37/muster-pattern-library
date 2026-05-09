# Local Truth Sheaf

## Intent

Have each unit report local truth and use a reducer to decide whether those facts glue into coherent machine state.

## When to use this

Use this as a small status reducer before attempting any logic-heavy orchestration.

## When not to use this

Do not use this to hide uncertainty behind a single fake health boolean.

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

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

Graduate toward Rare by standardizing fact schemas and proving real appliances can share them.
