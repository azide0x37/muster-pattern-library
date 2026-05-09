# Production-Beta Contract

The first production-beta target is Debian/Raspberry Pi OS with systemd.

Production beta means host-ready and mock-verifiable. It does not mean safe for unattended real hardware deployment.

## Filesystem Contract

```text
/etc/muster              reviewed configuration
/run/muster              runtime status and lock files
/run/muster/status.json  canonical health output
/var/lib/muster          durable local working data
/var/cache/muster        hot local cache
/mnt/muster/cold         lazily materialized cold storage
```

## Health Contract

The flagship appliance chain reports one of:

```text
healthy
degraded
failed
unknown
```

`unknown` is the safe default when a probe cannot make a defensible claim.

## Install Contract

Pattern `install.sh` scripts are dry-run by default. They may print the commands required to copy reviewed artifacts into `/etc/systemd/system` or `/usr/local/lib/muster`, but they must not mutate those locations unless invoked with `--apply`.

## Recovery Contract

Manual recovery enters through `muster-recover@.service`. Recovery should target the failing limb first and avoid whole-host reboot as the default response.

## Boot Contract

Network storage must not block boot. Mounts use lazy materialization, bounded timeouts, and `nofail`-style behavior.

## Device Conveyor Contract

A physical device event must hand off to systemd through udev `SYSTEMD_WANTS`; udev must not run the ingest itself.

Before ingest starts, the job must prove the destination capability and confirm enough hot-storage capacity. If capacity is temporarily unavailable because the hot/cold conveyor is still flushing, the job records `waiting_for_capacity`, runs a drain command or waits for the drain timer, and continues when capacity becomes available. If the timeout expires, it exits as a temporary failure and leaves inspectable state.
