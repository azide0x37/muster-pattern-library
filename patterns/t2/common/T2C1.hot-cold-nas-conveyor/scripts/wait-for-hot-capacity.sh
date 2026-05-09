#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Wait for enough hot-storage capacity. Default is dry-run mock mode; use --apply for real paths."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  hot_root=${HOT_ROOT:-/var/cache/muster/hot}
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-tc1-capacity}
  hot_root=${HOT_ROOT:-$mock_root/var/cache/muster/hot}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

min_bytes=${MIN_HOT_FREE_BYTES:-10737418240}
timeout_seconds=${CAPACITY_TIMEOUT_SECONDS:-900}
interval_seconds=${CAPACITY_INTERVAL_SECONDS:-5}
drain_command=${DRAIN_COMMAND:-}

mkdir -p "$hot_root" "$state_root"

available_bytes() {
  if [ "${MUSTER_MOCK_BACKPRESSURE:-0}" = "1" ] && [ ! -f "$state_root/capacity-ready" ]; then
    printf '%s\n' 0
    return
  fi
  df -Pk "$hot_root" | awk 'NR == 2 {printf "%.0f\n", $4 * 1024}'
}

write_state() {
  state=$1
  available=$2
  reason=$3
  printf '{"state":"%s","hot_root":"%s","available_bytes":%s,"required_bytes":%s,"reason":"%s"}\n' \
    "$state" "$hot_root" "$available" "$min_bytes" "$reason" > "$state_root/hot-capacity.json"
}

start=$(date +%s)
while :; do
  available=$(available_bytes)
  if [ "$available" -ge "$min_bytes" ]; then
    write_state healthy "$available" capacity_available
    printf '%s\n' "ok: hot capacity available"
    exit 0
  fi

  write_state degraded "$available" waiting_for_capacity
  now=$(date +%s)
  if [ "$((now - start))" -ge "$timeout_seconds" ]; then
    write_state failed "$available" capacity_timeout
    printf '%s\n' "failed: hot capacity timeout" >&2
    exit 75
  fi

  if [ -n "$drain_command" ]; then
    sh -c "$drain_command"
  fi
  sleep "$interval_seconds"
done
