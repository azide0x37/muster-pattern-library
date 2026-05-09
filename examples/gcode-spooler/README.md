# G-code Spooler

A safe mock-first spooler with inbox claiming, done/failed folders, fake sender behavior, serial binding stubs, and safety interlock placeholders.

## Pattern Map

- `TC2.dropfolder-spooler`
- `TR3.edge-control-plane`
- `R2.device-binding`

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
