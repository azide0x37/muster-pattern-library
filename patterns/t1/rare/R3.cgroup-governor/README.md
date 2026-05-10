# Cgroup Governor

## Intent

Constrain CPU, memory, IO, and restart behavior so one bad citizen cannot take down a small appliance.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this when a one-off shell command is clearer than a managed operational contract.

## System shape

Resource control directives sit next to restart policy and operator-facing limits.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` is a reviewed governed workload artifact.
- `scripts/cgroup-governed-run.sh` records the active resource policy in status JSON.
- `scripts/install.sh` installs reviewed artifacts in dry-run or staged-root mode.
- `scripts/doctor.sh` verifies resource-control directives and mocked status output.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Run `scripts/install.sh` to inspect the dry-run copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for a staged-root install.

## Verification

Run `scripts/doctor.sh`. The doctor verifies `CPUQuota`, `MemoryMax`, and `IOWeight`, then runs the governed workload helper in mock mode.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Review users, paths, credentials, sockets, and device permissions before deploying.

## Future work

No known blocker for the stable contract. Future variants can tune limits per workload without changing the base governance contract.
