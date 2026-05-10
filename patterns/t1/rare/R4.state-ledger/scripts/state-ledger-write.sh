#!/usr/bin/env sh
set -eu

apply=0
state=healthy
confidence=1.0
fact_key=example
fact_value=ok

usage() {
  printf '%s\n' "Write a Muster state ledger fact."
  printf '%s\n' "Default mode uses a mock root; use --apply for /run/muster and /var/lib/muster."
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) apply=1; shift ;;
    --state) state=${2:?missing state}; shift 2 ;;
    --confidence) confidence=${2:?missing confidence}; shift 2 ;;
    --fact) fact_key=${2:?missing fact key}; fact_value=${3:?missing fact value}; shift 3 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  root=${MUSTER_ROOT:-}
else
  root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-r4-ledger}
fi

state_root=${STATE_ROOT:-$root/run/muster}
ledger_dir=${LEDGER_DIR:-$root/var/lib/muster/state-ledger}
mkdir -p "$state_root" "$ledger_dir"

timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
boot_id=unknown
if [ -r /proc/sys/kernel/random/boot_id ]; then
  boot_id=$(cat /proc/sys/kernel/random/boot_id)
fi
session_id=${MUSTER_SESSION_ID:-manual}

event=$(printf '{"pattern":"R4.state-ledger","state":"%s","confidence":"%s","boot_id":"%s","session_id":"%s","timestamp":"%s","facts":{"%s":"%s"}}' \
  "$state" "$confidence" "$boot_id" "$session_id" "$timestamp" "$fact_key" "$fact_value")
printf '%s\n' "$event" > "$state_root/state-ledger.json"
printf '%s\n' "$event" >> "$ledger_dir/events.ndjson"
printf '%s\n' "ok: wrote state ledger event"
