#!/usr/bin/env sh
set -eu

subject=${1:-unknown}
apply=0
shift || true
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Record appliance recovery for SUBJECT. Default is dry-run mock mode."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-t3c1-recover}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$state_root"
printf '{"subject":"%s","state":"degraded","entrypoint":"muster-recover@.service"}\n' "$subject" > "$state_root/appliance-recovery.json"
printf '%s\n' "ok: appliance recovery recorded for $subject"
