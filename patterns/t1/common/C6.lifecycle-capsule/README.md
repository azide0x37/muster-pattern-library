# Lifecycle Capsule

## Intent

Install, verify, roll back, and cleanly uninstall one reviewed artifact bundle with a versioned release directory and a stable `current` pointer.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd. The lifecycle capsule generalizes the dvd-ingester install shape: staged roots use `MUSTER_ROOT`, installed code lives under `/opt/<project>/releases/<version>`, `/opt/<project>/current` points at the active generation, existing config under `/etc/<project>` is preserved, and rollback returns the pointer to the previous generation.

## When to use this

Use this when an appliance repo needs repeatable host installation without turning `/etc`, `/opt`, and systemd state into hand-managed drift.

## When not to use this

Do not use this for a single local script that does not need versioned releases, rollback, or clean uninstall behavior.

## System shape

The pattern has four operator entrypoints:

- `install.sh` copies a reviewed release into a versioned directory, preserves config, installs one unit, and switches `current`.
- `doctor.sh` proves the lifecycle in a temporary staged root.
- `rollback.sh` restores the previous `current` target.
- `uninstall.sh` removes owned installed artifacts while preserving config, durable state, and ledgers by default.

The lifecycle ledger lives under `/var/lib/muster/lifecycle/<project>/`.

## Subpatterns

None.

## Files

- `manifest.yaml` declares the pattern contract.
- `units/example.service` shows a unit that runs through the `current` pointer.
- `scripts/lifecycle-run.sh` is the mock installed workload.
- `scripts/install.sh`, `scripts/doctor.sh`, `scripts/rollback.sh`, and `scripts/uninstall.sh` implement the lifecycle.
- `examples/minimal/README.md` shows the smallest staged-root proof.

## Installation

Run `scripts/install.sh` without arguments first. It prints a dry-run plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for staged verification, or `scripts/install.sh --apply` as root on a target host.

## Verification

Run `scripts/doctor.sh`. It performs a staged install twice, proves config preservation, installs a second version, rolls back to the first version, and cleanly uninstalls artifacts while keeping config.

## Failure modes

Install fails before switching `current` if required source artifacts are missing. Rollback fails if no previous target was recorded. Uninstall preserves config by default, so stale config can affect a later reinstall unless the operator explicitly purges state.

## Rollback

Run `scripts/rollback.sh --apply`. It reads the lifecycle ledger and atomically replaces `current` with the prior release target.

## Security notes

Treat install and uninstall as privileged operations when `MUSTER_ROOT` is unset. Review project names, unit names, and target roots before applying on a real host.

## Future work

Add package-manager integration and stronger owner/group policy once Muster has a shared host user contract.
