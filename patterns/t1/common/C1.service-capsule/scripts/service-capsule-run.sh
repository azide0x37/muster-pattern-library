#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Run the service capsule workload. Default is dry-run mock mode; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-c1-run}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$state_root"
printf '%s\n' '{"service":"service-capsule","state":"healthy"}' > "$state_root/service-capsule.json"
printf '%s\n' "ok: wrote $state_root/service-capsule.json"
