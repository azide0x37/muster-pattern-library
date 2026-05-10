# Socket Anteroom

## Intent

Expose a local API or control endpoint through socket activation without keeping the backing service hot.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this for public network surfaces until authentication and binding are explicit.

## System shape

A small set of systemd-facing artifacts plus scripts and examples document the operational boundary.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` is a reviewed socket-activated service artifact.
- `units/muster-anteroom.socket` binds the local anteroom endpoint.
- `units/muster-anteroom.service` emits a bounded response through the activated socket.
- `scripts/socket-anteroom-serve.sh` writes status JSON and a local response.
- `scripts/install.sh` installs reviewed artifacts in dry-run or staged-root mode.
- `scripts/doctor.sh` checks units and proves the mocked responder.
- `examples/minimal/README.md` sketches a minimal usage.

## Installation

Run `scripts/install.sh` to inspect the dry-run copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for a staged-root install.

## Verification

Run `scripts/doctor.sh`. The doctor verifies the socket and service artifacts, runs the responder in mock mode, and checks the status JSON.

## Failure modes

Expected failures should leave inspectable logs, status files, or failed artifacts.

## Rollback

Disable related systemd units, stop any active services, remove copied artifacts from the target host, and leave runtime logs available for inspection.

## Security notes

Bind to localhost by default and treat every socket as an API surface.

## Future work

No known blocker for the stable contract. Future variants can add authenticated verbs while keeping localhost binding as the default.
