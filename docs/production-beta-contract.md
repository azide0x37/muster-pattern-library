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

Production-beta patterns declare lifecycle metadata in `manifest.yaml`. At minimum, they state supported install modes, doctor modes, rollback policy, uninstall policy, and update policy.

## Lifecycle Contract

Managed lifecycle patterns install code into versioned release directories and switch a stable `current` pointer:

```text
/opt/<project>/releases/<version>
/opt/<project>/current -> releases/<version>
/etc/<project>/<project>.env
/var/lib/muster/lifecycle/<project>
```

Repeated installs must preserve existing config and converge cleanly. Doctors should support staged or mock roots where practical. Clean uninstall removes owned installed artifacts by default; config, durable state, and ledgers require an explicit purge flag.

## Update Contract

Automatic updates are opt-in. The first update rail consumes a release manifest with `version`, `artifact_url`, and `sha256`, verifies the artifact, stages it under `/opt/<project>/releases/<version>`, switches `current`, and runs the active release doctor. If the doctor fails, the rail restores the previous `current` target.

## Recovery Contract

Manual recovery enters through `muster-recover@.service`. Recovery should target the failing limb first and avoid whole-host reboot as the default response.

## Boot Contract

Network storage must not block boot. Mounts use lazy materialization, bounded timeouts, and `nofail`-style behavior.

## Device Conveyor Contract

A physical device event must hand off to systemd through udev `SYSTEMD_WANTS`; udev must not run the ingest itself.

Before ingest starts, the job must prove the destination capability and confirm enough hot-storage capacity. If capacity is temporarily unavailable because the hot/cold conveyor is still flushing, the job records `waiting_for_capacity`, runs a drain command or waits for the drain timer, and continues when capacity becomes available. If the timeout expires, it exits as a temporary failure and leaves inspectable state.
