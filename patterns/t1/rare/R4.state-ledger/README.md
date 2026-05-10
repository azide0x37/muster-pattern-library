# State Ledger

## Intent

Make services explain themselves through journald and small runtime JSON facts under `/run/muster`.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

Services write concise facts with boot/session IDs, timestamps, and confidence values.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` is a reviewed ledger-writer service artifact.
- `scripts/state-ledger-write.sh` writes runtime status JSON and durable event lines.
- `scripts/install.sh` installs reviewed artifacts in dry-run or staged-root mode.
- `scripts/doctor.sh` proves mocked runtime and durable ledger writes.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Run `scripts/install.sh` to inspect the dry-run copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for a staged-root install.

## Verification

Run `scripts/doctor.sh`. The doctor writes a mock ledger event and verifies both runtime status and durable event files.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

No known blocker for the stable contract. Future variants can add richer fact schemas without changing the durable ledger boundary.
