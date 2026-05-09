# Intent-Bound Runtime

## Intent

Declare desired operational intent and let a disciplined runtime choose the service graph that satisfies it.

## When to use this

Use this when the capability needs to be repeatable across a small Linux appliance.

## When not to use this

Do not use this until the plain service graph is already reliable and observable.

## System shape

A small set of systemd-facing artifacts plus scripts and examples document the operational boundary.

## Subpatterns

- `M4.local-topos-runtime`
- `M5.temporal-sheaf`
- `TR3.edge-control-plane`
- `R5.capability-mount`

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

Intent runtimes must have strict policy boundaries around any action that changes machine state.

## Future work

Replace placeholders with hardware-specific checks and add integration tests as the pattern matures.
