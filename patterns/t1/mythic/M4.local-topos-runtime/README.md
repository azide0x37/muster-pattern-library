# Local Topos Runtime

## Intent

Treat targets as propositions, services as proofs, and observed paths or devices as evidence for valid local state.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

Practical kernel: evaluate a local proposition against explicit evidence. Minimum useful implementation: `scripts/topos-evaluate.sh` proves or rejects `evidence_exists` for a path. Full speculative version: policy-bound logic over targets, services, and observed devices. De-mythicize it as evidence-gated local policy.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` runs the evidence evaluator.
- `scripts/topos-evaluate.sh` records proposition truth from a concrete evidence path.
- `scripts/install.sh` installs reviewed artifacts in dry-run or staged-root mode.
- `scripts/doctor.sh` checks the unit and proves mock evidence evaluation.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Run `scripts/install.sh` to inspect the dry-run copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for a staged-root install.

## Verification

Run `scripts/doctor.sh`. The doctor creates mock evidence and verifies `local-topos-runtime.json`.

## Failure modes

Absent evidence fails the proposition and records the evidence path that was checked.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Keep any actuator behind explicit policy; logic engines should not gain ambient authority.

## Future work

No known blocker for the stable minimal kernel. Future work is binding propositions to explicit policy files.
