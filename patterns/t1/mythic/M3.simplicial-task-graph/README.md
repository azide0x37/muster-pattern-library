# Simplicial Task Graph

## Intent

Model target states as filled dependency shapes where missing faces explain why the desired state cannot exist.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this where ordinary target dependencies and health checks explain enough.

## System shape

Practical kernel: name the required faces of a task and report which ones are missing. Minimum useful implementation: `scripts/task-graph-evaluate.sh` compares required faces with present faces and records an explanation. Full speculative version: derived dependency shapes across many services. De-mythicize it as explainable readiness checking.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` runs the task graph evaluator.
- `scripts/task-graph-evaluate.sh` records missing dependency faces.
- `scripts/install.sh` installs reviewed artifacts in dry-run or staged-root mode.
- `scripts/doctor.sh` checks the unit and proves a complete mocked graph.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Run `scripts/install.sh` to inspect the dry-run copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for a staged-root install.

## Verification

Run `scripts/doctor.sh`. The doctor runs a complete mock graph and verifies `simplicial-task-graph.json`.

## Failure modes

Missing faces degrade the graph and must be listed in status output rather than hidden behind a generic failure.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

No known blocker for the stable minimal kernel. Future work is deriving faces from real units and target dependencies.
