#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Check whether a local state loop returns to its starting state."
      printf '%s\n' "Set HOLONOMY_STEPS to a space-separated loop; default is closed and healthy."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  root=${MUSTER_ROOT:-}
else
  root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-m2-holonomy}
fi

state_root=${STATE_ROOT:-$root/run/muster}
mkdir -p "$state_root"

steps=${HOLONOMY_STEPS:-"idle mounted checked idle"}
first=
last=
count=0
for step in $steps; do
  if [ -z "$first" ]; then
    first=$step
  fi
  last=$step
  count=$((count + 1))
done

state=degraded
if [ "$count" -gt 1 ] && [ "$first" = "$last" ]; then
  state=healthy
fi

printf '{"pattern":"M2.holonomy-detector","state":"%s","steps":%s,"start":"%s","end":"%s"}\n' \
  "$state" "$count" "$first" "$last" > "$state_root/holonomy-detector.json"

[ "$state" = "healthy" ] || exit 75
