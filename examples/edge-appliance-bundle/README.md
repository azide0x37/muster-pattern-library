# Edge Appliance Bundle

A baseline Pi-style appliance with local service management, lazy storage, scheduled status, bounded recovery, and outward state publishing.

## Pattern Map

- `T3C1.edge-appliance-bundle`
- `T2C1.hot-cold-nas-conveyor`
- `T2C3.scheduled-herald`
- `T2C4.self-healing-reconnector`
- `T2C5.local-sidecar-bridge`

## Architecture

```text
operator input -> local queue/control plane -> managed services -> status ledger -> outward report
```

## Mock Mode

Keep the first pass mocked. Run the dependency scripts without `--apply` so they use a temporary `MUSTER_MOCK_ROOT`; then run `patterns/t3/common/T3C1.edge-appliance-bundle/scripts/doctor.sh` to verify the assembled target shape. Only the target host should use `--apply`.

## Success Criteria

- The example maps every moving part to a Muster pattern ID.
- Failure leaves inspectable files or status.
- Real hardware actuation is absent by default.
- `status.json` exists in the mock runtime root and reports one of `healthy`, `degraded`, `failed`, or `unknown`.
