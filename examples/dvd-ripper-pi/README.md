# DVD Ripper Pi

A user-owned-media workflow sketch that keeps commands as placeholders, sends output through hot/cold storage, and reports status through Herald.

## Pattern Map

- `C1.service-capsule`
- `C2.persistent-tick`
- `C3.dropfolder-trigger`
- `C4.lazy-resource-gate`
- `C5.failure-ratchet`
- `TC1.hot-cold-nas-conveyor`
- `TC2.dropfolder-spooler`
- `TC3.scheduled-herald`
- `T3C1.edge-appliance-bundle`

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
