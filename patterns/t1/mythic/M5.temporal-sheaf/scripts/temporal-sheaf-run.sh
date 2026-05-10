#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Record a persisted temporal obligation and current runtime snapshot."
      printf '%s\n' "Default mode uses a mock root; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  root=${MUSTER_ROOT:-}
else
  root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-m5-temporal}
fi

state_root=${STATE_ROOT:-$root/run/muster}
durable_dir=${TEMPORAL_DURABLE_DIR:-$root/var/lib/muster/temporal-sheaf}
mkdir -p "$state_root" "$durable_dir"

obligation=${TEMPORAL_OBLIGATION:-reconcile-after-boot}
timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
ledger="$durable_dir/obligations.ndjson"
prior=0
if [ -f "$ledger" ]; then
  prior=$(wc -l < "$ledger" | tr -d ' ')
fi

printf '{"obligation":"%s","observed_at":"%s"}\n' "$obligation" "$timestamp" >> "$ledger"
carried=$((prior + 1))
printf '{"pattern":"M5.temporal-sheaf","state":"healthy","obligation":"%s","carried_obligations":%s,"observed_at":"%s"}\n' \
  "$obligation" "$carried" "$timestamp" > "$state_root/temporal-sheaf.json"

printf '%s\n' "ok: temporal obligation recorded"
