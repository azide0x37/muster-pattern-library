# Edge Appliance Bundle

A baseline Pi-style appliance with local service management, lazy storage, scheduled status, bounded recovery, and outward state publishing.

## Pattern Map

- `T3C1.edge-appliance-bundle`
- `TC1.hot-cold-nas-conveyor`
- `TC3.scheduled-herald`
- `TC4.self-healing-reconnector`
- `TC5.local-sidecar-bridge`

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
