# Bluetooth Audio Gateway

A Bluetooth audio appliance that distinguishes device visibility, connection, sink routing, playback, and Home Assistant visibility.

## Pattern Map

- `TR1.bluetooth-audio-gateway`
- `T3R1.multi-resource-orchestrator`
- `R2.device-binding`
- `R4.state-ledger`

## Architecture

```text
operator input -> local queue/control plane -> managed services -> status ledger -> outward report
```

## Mock Mode

Keep the first pass mocked. Replace hardware commands with `printf`, local files, and fake status payloads until the lifecycle is visible.

## Success Criteria

- The example maps every moving part to a Muster pattern ID.
- Failure leaves inspectable files or status.
- Real hardware actuation is absent by default.
