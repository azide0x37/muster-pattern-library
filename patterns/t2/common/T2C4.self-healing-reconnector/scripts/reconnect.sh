#!/usr/bin/env sh
set -eu

resource=${1:-example}
case "$resource" in
  --help|-h)
    printf '%s\n' "Run a bounded reconnect attempt. Default is dry-run mock mode; pass RESOURCE --apply for real state."
    exit 0
    ;;
esac

apply=0
max_attempts=${MAX_ATTEMPTS:-3}
cooldown_seconds=${COOLDOWN_SECONDS:-2}
shift || true
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Run a bounded reconnect attempt. Default is dry-run mock mode; pass RESOURCE --apply for real state."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-tc4-reconnect}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$state_root"
attempt=1
while [ "$attempt" -le "$max_attempts" ]; do
  printf '%s\n' "attempt $attempt/$max_attempts for $resource"
  if [ "$apply" -eq 0 ]; then
    break
  fi
  sleep "$cooldown_seconds"
  attempt=$((attempt + 1))
done

printf '{"resource":"%s","state":"degraded","attempts":%s,"cooldown_seconds":%s}\n' "$resource" "$attempt" "$cooldown_seconds" > "$state_root/reconnector-$resource.json"
printf '%s\n' "ok: wrote $state_root/reconnector-$resource.json"
