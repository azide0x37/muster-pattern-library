# Local Truth Sheaf

## Intent

Have each unit report local truth and use a reducer to decide whether those facts glue into coherent machine state.

## When to use this

Use this as a small status reducer before attempting any logic-heavy orchestration.

## When not to use this

Do not use this to hide uncertainty behind a single fake health boolean.

## System shape

Practical kernel: collect local JSON facts and reduce them to a defensible machine-state claim. Minimum useful implementation: `scripts/local-truth-reduce.sh` counts healthy, degraded, unknown, and failed facts under a mockable state root. Full speculative version: typed fact sheaves shared across many services. De-mythicize it by treating the reducer as a conservative health aggregator with explicit uncertainty.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` runs the local truth reducer.
- `scripts/local-truth-reduce.sh` reduces fact files into status JSON.
- `scripts/install.sh` installs reviewed artifacts in dry-run or staged-root mode.
- `scripts/doctor.sh` checks the unit and proves a mocked reduction.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Run `scripts/install.sh` to inspect the dry-run copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for a staged-root install.

## Verification

Run `scripts/doctor.sh`. The doctor runs the reducer in mock mode and verifies `local-truth-sheaf.json`.

## Failure modes

The reducer must preserve uncertainty. Missing facts produce a safe local default; failed facts dominate the reduced state.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Do not let a reducer invent authority. Inputs should be local, inspectable facts from services that already own their resources.

## Future work

No known blocker for the stable minimal kernel. Future work is standardizing shared fact schemas across composed patterns.
