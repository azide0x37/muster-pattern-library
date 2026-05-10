# Holonomy Detector

## Intent

Run a loop through expected states and detect whether the system actually returns to identity.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

Practical kernel: run a loop through named local states and verify that the final state equals the start. Minimum useful implementation: `scripts/holonomy-check.sh` evaluates a declared state loop and records drift. Full speculative version: richer checks over mounts, processes, devices, and queues. De-mythicize it as a conservative loop invariant check.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` runs the holonomy check.
- `scripts/holonomy-check.sh` evaluates a state loop and records status JSON.
- `scripts/install.sh` installs reviewed artifacts in dry-run or staged-root mode.
- `scripts/doctor.sh` checks the unit and proves a closed mocked loop.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Run `scripts/install.sh` to inspect the dry-run copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for a staged-root install.

## Verification

Run `scripts/doctor.sh`. The doctor runs a closed mock loop and verifies `holonomy-detector.json`.

## Failure modes

Failed loops indicate leaked mounts, stuck devices, ghost processes, or inconsistent state.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

No known blocker for the stable minimal kernel. Future work is attaching loop steps to real device and mount probes.
