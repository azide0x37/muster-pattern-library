# Minimal Device-Triggered Conveyor

This sketch models an optical-drive ingest appliance without assuming DVD-specific tooling.

```text
device change event
  -> udev adds SYSTEMD_WANTS=muster-device-conveyor@%k.service
  -> systemd runs one bounded job for /dev/%I
  -> capability path is proved
  -> hot-storage capacity is awaited
  -> local output is staged
  -> TC1 hot/cold conveyor publishes cold
```

Run `scripts/doctor.sh` to exercise the backpressure path in mock mode.
