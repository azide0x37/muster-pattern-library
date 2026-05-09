#!/usr/bin/env sh
set -eu

apply=0
once=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    --once) once=1 ;;
    -h|--help)
      printf '%s\n' "Check the edge appliance bundle. Default is dry-run mock mode; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-t3c1-doctor-run}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$state_root"
status_file="$state_root/status.json"
if [ -s "$status_file" ]; then
  state=healthy
else
  state=unknown
  printf '%s\n' '{"state":"unknown","facts":{}}' > "$status_file"
fi

printf '{"machine":"muster-edge","role":"edge-appliance-bundle","state":"%s","once":%s}\n' "$state" "$once" > "$state_root/appliance.json"
printf '%s\n' "ok: appliance state $state"
