#!/usr/bin/env sh
set -eu

root=${MUSTER_ROOT:-}
apply=0
state_dir="$root/run/muster/home-assistant-mqtt-bridge"
outbox_dir=${MQTT_OUTBOX_DIR:-$state_dir/mqtt-outbox}
ledger_dir=${LEDGER_DIR:-$root/var/lib/muster/home-assistant-mqtt-bridge}
state_file="$state_dir/state.json"
last_state="$ledger_dir/last-state.json"
last_topic="$ledger_dir/last-topic"

usage() {
  printf '%s\n' "Rollback T2R6.home-assistant-mqtt-bridge to the previous published state."
  printf '%s\n' "Default mode is dry-run; use --apply to restore state and queue a replacement MQTT payload."
  printf '%s\n' "Set MUSTER_ROOT for staged-root rollback."
}

for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ ! -f "$last_state" ]; then
  printf '%s\n' "no previous bridge state recorded: $last_state" >&2
  exit 1
fi

if [ "$apply" -eq 1 ] && [ -z "$root" ] && [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "--apply requires root unless MUSTER_ROOT is set." >&2
  exit 1
fi

topic_file() {
  printf '%s' "$1" | tr '/+' '__'
}

topic=$(cat "$last_topic" 2>/dev/null || printf '%s\n' "muster/home-assistant-mqtt-bridge/enabled/state")

if [ "$apply" -eq 1 ]; then
  mkdir -p "$state_dir" "$outbox_dir"
  cp "$last_state" "$state_file"
  cp "$last_state" "$outbox_dir/$(topic_file "$topic").json"
  printf '%s\t%s\n' "$topic" "$outbox_dir/$(topic_file "$topic").json" >> "$outbox_dir/topics.log"
else
  printf '%s\n' "dry-run: restore $state_file from $last_state"
fi

printf '%s\n' "rollback plan complete for T2R6.home-assistant-mqtt-bridge"
