# Minimal T2R6 Home Assistant MQTT Bridge

This sketch shows the smallest local artifact set for `T2R6.home-assistant-mqtt-bridge`.

Start in mock mode:

```sh
patterns/t2/rare/T2R6.home-assistant-mqtt-bridge/scripts/ha-mqtt-bridge.sh --once
```

The first run writes Home Assistant discovery and state payloads under a mock `mqtt-outbox/` directory. A Home Assistant command can be tested by writing `ON` or `OFF` to `mqtt-control/relay.cmd`, then running `scripts/ha-mqtt-bridge.sh --control`.

Use `MUSTER_ROOT=/tmp/root scripts/install.sh --apply` for staged-root verification before copying the reviewed service and timer onto a host.
