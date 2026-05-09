#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Run the protected job. Default is dry-run mock mode; set MUSTER_FAIL=1 to exercise recovery."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "${MUSTER_FAIL:-0}" = "1" ]; then
  printf '%s\n' "simulated protected job failure" >&2
  exit 1
fi

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-c5-job}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$state_root"
printf '%s\n' '{"job":"failure-prone-job","state":"healthy"}' > "$state_root/failure-ratchet.json"
printf '%s\n' "ok: protected job completed"
