# Temporal Sheaf

## Intent

Glue persistent timers, snapshots, and boot/session facts so machines remember obligations across downtime.

## When to use this

Use this where a machine sleeps, reboots, or roams but still owes work after returning.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

Practical kernel: persist obligations and current runtime snapshots so work owed before downtime is still visible after return. Minimum useful implementation: `scripts/temporal-sheaf-run.sh` appends durable obligation events and records runtime status. Full speculative version: temporal joins across timers, boot sessions, and service state. De-mythicize it as durable obligation tracking.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` runs the temporal obligation tracker.
- `scripts/temporal-sheaf-run.sh` records durable obligations and runtime status.
- `scripts/install.sh` installs reviewed artifacts in dry-run or staged-root mode.
- `scripts/doctor.sh` checks the unit and proves repeated mocked obligation writes.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Run `scripts/install.sh` to inspect the dry-run copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for a staged-root install.

## Verification

Run `scripts/doctor.sh`. The doctor records two mock obligations and verifies runtime and durable files.

## Failure modes

A missing durable directory or unwritable runtime status path must fail visibly and leave the attempted obligation in logs.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

No known blocker for the stable minimal kernel. Future work is joining obligations with real persistent timers and boot session facts.
