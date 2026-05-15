#!/usr/bin/env sh
set -eu

root=${MUSTER_ROOT:-}
apply=0
purge_state=0
unit_dir="$root/etc/systemd/system"
lib_dir="$root/usr/local/lib/muster/home-assistant-mqtt-bridge"
config_file="$root/etc/muster/home-assistant-mqtt-bridge.env"
state_dir="$root/run/muster/home-assistant-mqtt-bridge"
ledger_dir="$root/var/lib/muster/home-assistant-mqtt-bridge"

usage() {
  printf '%s\n' "Cleanly uninstall T2R6.home-assistant-mqtt-bridge artifacts."
  printf '%s\n' "Default mode is dry-run; use --apply to remove bridge units and scripts."
  printf '%s\n' "Config, state, and ledgers are preserved unless --purge-state is explicit."
}

for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    --purge-state) purge_state=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ] && [ -z "$root" ] && [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "--apply requires root unless MUSTER_ROOT is set." >&2
  exit 1
fi

remove_path() {
  if [ "$apply" -eq 1 ]; then
    rm -rf "$1"
  else
    printf '%s\n' "dry-run: remove $1"
  fi
}

remove_path "$unit_dir/muster-ha-mqtt-bridge.service"
remove_path "$unit_dir/muster-ha-mqtt-bridge.timer"
remove_path "$lib_dir"

if [ "$purge_state" -eq 1 ]; then
  remove_path "$config_file"
  remove_path "$state_dir"
  remove_path "$ledger_dir"
else
  printf '%s\n' "preserve bridge config, runtime state, and lifecycle ledger"
fi

printf '%s\n' "uninstall plan complete for T2R6.home-assistant-mqtt-bridge"
