#!/usr/bin/env sh
set -eu

device=${1:-/dev/mock0}
apply=0
shift || true
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Run one device-triggered conveyor ingest. Default is dry-run mock mode; use --apply for real paths."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
  base_root=${BASE_ROOT:-/var/lib/muster/device-conveyor}
  hot_root=${HOT_ROOT:-/var/cache/muster/hot}
  capability_path=${CAPABILITY_PATH:-/mnt/muster/cold}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-tr4-device-conveyor}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
  base_root=${BASE_ROOT:-$mock_root/var/lib/muster/device-conveyor}
  hot_root=${HOT_ROOT:-$mock_root/var/cache/muster/hot}
  capability_path=${CAPABILITY_PATH:-$mock_root/mnt/muster/cold}
fi

capability_name=${CAPABILITY_NAME:-cold-storage}
min_hot_free_bytes=${MIN_HOT_FREE_BYTES:-10737418240}
capacity_timeout_seconds=${CAPACITY_TIMEOUT_SECONDS:-900}
capacity_interval_seconds=${CAPACITY_INTERVAL_SECONDS:-5}
ingest_command=${INGEST_COMMAND:-}
device_name=$(basename "$device" | tr -cd 'A-Za-z0-9._-' | cut -c1-64)
device_name=${device_name:-device}
run_id="${device_name}-$(date -u '+%Y%m%dT%H%M%SZ')"
run_dir="$base_root/work/$run_id"
handoff_dir="$hot_root/device-conveyor"
lock_file="$state_root/device-conveyor.lock"

mkdir -p "$state_root" "$base_root/work" "$handoff_dir" "$capability_path"

write_state() {
  state=$1
  reason=$2
  printf '{"device":"%s","run_id":"%s","state":"%s","reason":"%s","run_dir":"%s"}\n' \
    "$device" "$run_id" "$state" "$reason" "$run_dir" > "$state_root/device-conveyor.json"
}

require_capability() {
  if [ "$apply" -eq 1 ] && command -v findmnt >/dev/null 2>&1 && ! findmnt "$capability_path" >/dev/null 2>&1; then
    write_state degraded capability_not_mounted
    printf '%s\n' "degraded: capability path is not mounted: $capability_path" >&2
    exit 75
  fi
  if [ ! -d "$capability_path" ] || [ ! -w "$capability_path" ]; then
    write_state failed capability_unavailable
    printf '%s\n' "failed: capability path is not writable: $capability_path" >&2
    exit 1
  fi
}

wait_for_hot_capacity() {
  wait_script=${WAIT_FOR_HOT_CAPACITY:-}
  if [ -z "$wait_script" ]; then
    candidate=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." 2>/dev/null && pwd)/t2/common/T2C1.hot-cold-nas-conveyor/scripts/wait-for-hot-capacity.sh
    if [ -x "$candidate" ]; then
      wait_script=$candidate
    fi
  fi

  if [ -n "$wait_script" ] && [ -x "$wait_script" ]; then
    MUSTER_MOCK_ROOT="${MUSTER_MOCK_ROOT:-}" HOT_ROOT="$hot_root" STATE_ROOT="$state_root" MIN_HOT_FREE_BYTES="$min_hot_free_bytes" CAPACITY_TIMEOUT_SECONDS="$capacity_timeout_seconds" CAPACITY_INTERVAL_SECONDS="$capacity_interval_seconds" DRAIN_COMMAND="${DRAIN_COMMAND:-}" MUSTER_MOCK_BACKPRESSURE="${MUSTER_MOCK_BACKPRESSURE:-0}" "$wait_script"
    return
  fi

  available=$(df -Pk "$hot_root" | awk 'NR == 2 {printf "%.0f\n", $4 * 1024}')
  if [ "$available" -lt "$min_hot_free_bytes" ]; then
    write_state degraded waiting_for_capacity
    printf '%s\n' "degraded: not enough hot-storage capacity" >&2
    exit 75
  fi
}

run_ingest() {
  mkdir -p "$run_dir"
  touch "$run_dir/.ingest-in-progress"
  if [ -n "$ingest_command" ]; then
    DEVICE="$device" RUN_DIR="$run_dir" sh -c "$ingest_command"
  else
    printf 'mock ingest from %s\n' "$device" > "$run_dir/payload.txt"
  fi
  rm -f "$run_dir/.ingest-in-progress"
  touch "$run_dir/.ingest-complete"
}

handoff_to_conveyor() {
  target="$handoff_dir/$run_id"
  rm -rf "$target"
  mv "$run_dir" "$target"
  printf '{"device":"%s","run_id":"%s","state":"ready_for_cold_publish","handoff":"%s"}\n' "$device" "$run_id" "$target" > "$state_root/device-conveyor-handoff.json"
}

if command -v flock >/dev/null 2>&1; then
  exec 9>"$lock_file"
  if ! flock -n 9; then
    write_state degraded already_running
    printf '%s\n' "degraded: another device conveyor job is running" >&2
    exit 75
  fi
else
  lock_dir="$state_root/device-conveyor.lockdir"
  if ! mkdir "$lock_dir" 2>/dev/null; then
    write_state degraded already_running
    printf '%s\n' "degraded: another device conveyor job is running" >&2
    exit 75
  fi
  trap 'rmdir "$lock_dir" 2>/dev/null || true' EXIT INT TERM
fi

write_state degraded starting
if ! require_capability; then
  exit 1
fi
wait_for_hot_capacity

if ! run_ingest; then
  rm -f "$run_dir/.ingest-in-progress"
  touch "$run_dir/.ingest-failed"
  write_state failed ingest_failed
  exit 1
fi

handoff_to_conveyor
write_state healthy ready_for_cold_publish
printf '%s\n' "ok: device-triggered conveyor staged $run_id"
