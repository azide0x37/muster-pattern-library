#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Run one persistent tick. Default is dry-run mock mode; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-c2-tick}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$state_root"
now=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
printf '{"job":"persistent-tick","state":"healthy","ran_at":"%s"}\n' "$now" > "$state_root/persistent-tick.json"
printf '%s\n' "ok: wrote $state_root/persistent-tick.json"
