# Signed Update Rail

## Intent

Poll a release manifest, verify the release artifact, promote it through the lifecycle capsule, and roll back when the post-update doctor fails.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd timers. The first implementation follows the dvd-ingester update rail: `AUTOUPDATE=0` disables polling, `UPDATE_MANIFEST_URL` points at a release manifest, artifacts are checked with SHA256 before extraction, `/opt/<project>/current` is switched only after staging, and the active release doctor is the promotion gate.

## When to use this

Use this when a local appliance should receive reviewed release artifacts without an operator running `git pull` on the device.

## When not to use this

Do not use this when the appliance cannot tolerate unattended replacement of installed code, or when release artifacts are not immutable and hash-addressable.

## System shape

`muster-signed-update.timer` periodically starts `muster-signed-update.service`. The service runs `scripts/update.sh`, which reads a release manifest, verifies the artifact hash, extracts the new release under `/opt/<project>/releases/<version>`, switches `current`, runs the release doctor, and restores the previous pointer when the doctor fails.

## Subpatterns

- `C2.persistent-tick`
- `C5.failure-ratchet`
- `C6.lifecycle-capsule`
- `R4.state-ledger`

## Files

- `manifest.yaml` declares the pattern contract.
- `units/muster-signed-update.*` show the polling rail.
- `scripts/update.sh` implements manifest fetch, hash verification, promotion, and rollback.
- `scripts/rollback.sh` and `scripts/uninstall.sh` provide operator lifecycle controls.
- `scripts/install.sh` and `scripts/doctor.sh` provide dry-run install and mock verification.

## Installation

Run `scripts/install.sh` without arguments first. It prints the update service, timer, and helper copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for staged verification, or `scripts/install.sh --apply` as root after configuring `/etc/muster/signed-update.env`.

## Verification

Run `scripts/doctor.sh`. It creates a staged appliance root, promotes a passing update, then attempts a failing update and proves the `current` pointer rolls back.

## Failure modes

Missing manifest fields, bad hashes, failed downloads, extraction errors, and failed doctors all fail before declaring the update healthy. A failed doctor after promotion restores the previous release when one exists.

## Rollback

Run `scripts/rollback.sh --apply` to restore the previous target recorded by the update rail. Automatic rollback uses the same pointer-switching behavior after a failed doctor gate.

## Security notes

This pattern currently verifies artifact SHA256 from the manifest. Production deployments should publish immutable release assets and add detached manifest signatures before marking the rail stable.

## Future work

Add signature verification policy, release retention limits, and state-ledger event output for update attempts.
