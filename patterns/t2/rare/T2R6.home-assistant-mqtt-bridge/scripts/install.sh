#!/usr/bin/env sh
set -eu

root=${MUSTER_ROOT:-}
apply=0
unit_dir="$root/etc/systemd/system"
lib_dir="$root/usr/local/lib/muster/home-assistant-mqtt-bridge"
config_dir="$root/etc/muster"
config_file="$config_dir/home-assistant-mqtt-bridge.env"

usage() {
  printf '%s\n' "Install T2R6.home-assistant-mqtt-bridge artifacts."
  printf '%s\n' "Default mode is dry-run; use --apply to copy files."
  printf '%s\n' "Set MUSTER_ROOT to perform a staged-root install without touching the host."
}

for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

run() {
  if [ "$apply" -eq 1 ]; then
    "$@"
  else
    printf 'dry-run:'
    printf ' %s' "$@"
    printf '\n'
  fi
}

if [ "$apply" -eq 1 ] && [ -z "$root" ] && [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "--apply requires root unless MUSTER_ROOT is set." >&2
  exit 1
fi

run install -d -m 0755 "$unit_dir" "$lib_dir" "$config_dir"
run install -m 0644 "$pattern_dir/units/muster-ha-mqtt-bridge.service" "$unit_dir/muster-ha-mqtt-bridge.service"
run install -m 0644 "$pattern_dir/units/muster-ha-mqtt-bridge.timer" "$unit_dir/muster-ha-mqtt-bridge.timer"
run install -m 0755 "$pattern_dir/scripts/ha-mqtt-bridge.sh" "$lib_dir/ha-mqtt-bridge.sh"
run install -m 0755 "$pattern_dir/scripts/rollback.sh" "$lib_dir/rollback.sh"
run install -m 0755 "$pattern_dir/scripts/uninstall.sh" "$lib_dir/uninstall.sh"

if [ "$apply" -eq 1 ]; then
  if [ ! -f "$config_file" ]; then
    {
      printf 'HA_NODE_ID=muster_bridge\n'
      printf 'HA_DEVICE_NAME=Muster Home Assistant MQTT Bridge\n'
      printf 'HA_DISCOVERY_PREFIX=homeassistant\n'
      printf 'MQTT_BASE_TOPIC=muster/home-assistant-mqtt-bridge\n'
      printf 'MQTT_OUTBOX_DIR=\n'
      printf 'MQTT_CONTROL_DIR=\n'
    } > "$config_file"
    chmod 0644 "$config_file"
  fi
else
  printf '%s\n' "dry-run: preserve or create $config_file"
fi

printf '%s\n' "install plan complete for T2R6.home-assistant-mqtt-bridge"
