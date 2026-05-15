# Home Assistant MQTT Bridge

## Intent

Publish Home Assistant MQTT discovery payloads, bridge local appliance state into MQTT-style topics, and consume bounded Home Assistant control commands without requiring a broker during validation.

## Production beta contract

Target platform is Debian/Raspberry Pi OS with systemd timers. The beta artifact is deliberately mockable: discovery, state, and command traffic are represented as files under `mqtt-outbox/` and `mqtt-control/` until a deployment supplies reviewed broker plumbing. Discovery uses a single Home Assistant MQTT device payload with status sensors, a restart button, and an enabled switch. The bridge only accepts tokenized entity names plus allowlisted `enabled` and `restart` control payloads by default.

## When to use this

Use this when an appliance should appear in Home Assistant through MQTT discovery and expose a narrow control surface that can be proven locally before connecting to a real broker.

## When not to use this

Do not use this when the appliance needs arbitrary Home Assistant entities, templated payloads, retained MQTT credentials in the repository, or unaudited command topics.

## System shape

`muster-ha-mqtt-bridge.timer` periodically starts `muster-ha-mqtt-bridge.service`. The service runs `scripts/ha-mqtt-bridge.sh --once --apply`, which emits one Home Assistant device discovery payload, publishes the current enabled state, and processes any pending command file from the control inbox.

## Subpatterns

- `C1.service-capsule`
- `C2.persistent-tick`
- `C5.failure-ratchet`
- `C6.lifecycle-capsule`
- `R4.state-ledger`
- `T2C5.local-sidecar-bridge`

## Files

- `manifest.yaml` declares the pattern contract.
- `units/muster-ha-mqtt-bridge.*` show the periodic bridge service.
- `scripts/ha-mqtt-bridge.sh` implements mockable discovery, state publish, and control handling.
- `scripts/rollback.sh` restores the previous published state.
- `scripts/uninstall.sh` removes installed artifacts while preserving state by default.
- `scripts/install.sh` and `scripts/doctor.sh` provide dry-run install and mock verification.

## Installation

Run `scripts/install.sh` without arguments first. It prints the service, timer, helper, and config copy plan. Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for staged verification, or `scripts/install.sh --apply` as root after configuring `/etc/muster/home-assistant-mqtt-bridge.env`.

## Verification

Run `scripts/doctor.sh`. It writes a mocked Home Assistant device discovery payload, publishes enabled state, processes `OFF` and restart control commands, and proves rollback restores the previous state.

## Failure modes

Malformed entity names, unsupported control payloads, missing previous state, missing installed files, and invalid unit files fail closed. The mock outbox preserves topic-to-file mappings in `topics.log` for operator inspection.

## Rollback

Run `scripts/rollback.sh --apply` with `MUSTER_ROOT` for a staged root or as root on the target host. Rollback restores the previous `state.json` snapshot and queues a replacement MQTT state payload.

## Security notes

Broker credentials are intentionally outside the repository. Keep command topics narrow, map each command to an explicit local action, and do not enable real broker publishing until the deployment has credential storage, TLS, and command authorization reviewed.

## Future work

Add a broker adapter with TLS-only defaults, support more entity classes, and emit state-ledger events for every discovery, state, control, and rollback action.
