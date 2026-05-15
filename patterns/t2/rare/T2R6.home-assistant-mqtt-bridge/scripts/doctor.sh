#!/usr/bin/env sh
set -eu

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/muster-ha-mqtt-bridge.service"
test -f "$pattern_dir/units/muster-ha-mqtt-bridge.timer"
test -x "$pattern_dir/scripts/ha-mqtt-bridge.sh"
test -x "$pattern_dir/scripts/install.sh"
test -x "$pattern_dir/scripts/rollback.sh"
test -x "$pattern_dir/scripts/uninstall.sh"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/muster-ha-mqtt-bridge.service" "$pattern_dir/units/muster-ha-mqtt-bridge.timer"
fi

mock_root=$(mktemp -d "${TMPDIR:-/tmp}/muster-t2r6-doctor.XXXXXX")
cleanup() {
  rm -rf "$mock_root"
}
trap cleanup EXIT INT TERM

MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/ha-mqtt-bridge.sh" --discover >/dev/null
test -s "$mock_root/run/muster/home-assistant-mqtt-bridge/mqtt-outbox/homeassistant_device_muster_bridge_config.json"
grep '"restart_service"' "$mock_root/run/muster/home-assistant-mqtt-bridge/mqtt-outbox/homeassistant_device_muster_bridge_config.json" >/dev/null
grep '"enabled"' "$mock_root/run/muster/home-assistant-mqtt-bridge/mqtt-outbox/homeassistant_device_muster_bridge_config.json" >/dev/null

MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/ha-mqtt-bridge.sh" --state enabled ON >/dev/null
grep '"state":"ON"' "$mock_root/run/muster/home-assistant-mqtt-bridge/state.json" >/dev/null

printf '%s\n' "OFF" > "$mock_root/run/muster/home-assistant-mqtt-bridge/mqtt-control/enabled.cmd"
MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/ha-mqtt-bridge.sh" --control >/dev/null
grep '"state":"OFF"' "$mock_root/run/muster/home-assistant-mqtt-bridge/state.json" >/dev/null
test -f "$mock_root/run/muster/home-assistant-mqtt-bridge/mqtt-control/enabled.cmd.processed"

printf '%s\n' "PRESS" > "$mock_root/run/muster/home-assistant-mqtt-bridge/mqtt-control/restart.cmd"
MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/ha-mqtt-bridge.sh" --control >/dev/null
grep '"control":"restart"' "$mock_root/run/muster/home-assistant-mqtt-bridge/control-result.json" >/dev/null

MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/ha-mqtt-bridge.sh" --state enabled ON >/dev/null
MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/ha-mqtt-bridge.sh" --state enabled OFF >/dev/null
MUSTER_ROOT="$mock_root" "$pattern_dir/scripts/rollback.sh" --apply >/dev/null
grep '"state":"ON"' "$mock_root/run/muster/home-assistant-mqtt-bridge/state.json" >/dev/null

printf '%s\n' "ok: T2R6.home-assistant-mqtt-bridge"
