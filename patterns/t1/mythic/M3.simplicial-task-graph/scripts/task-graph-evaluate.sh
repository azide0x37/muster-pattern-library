#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Evaluate whether required task faces are present."
      printf '%s\n' "Set REQUIRED_FACES and PRESENT_FACES as space-separated face names."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  root=${MUSTER_ROOT:-}
else
  root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-m3-graph}
fi

state_root=${STATE_ROOT:-$root/run/muster}
mkdir -p "$state_root"

required=${REQUIRED_FACES:-"input worker output"}
present=${PRESENT_FACES:-$required}
missing=
missing_count=0

for face in $required; do
  found=0
  for have in $present; do
    if [ "$face" = "$have" ]; then
      found=1
    fi
  done
  if [ "$found" -eq 0 ]; then
    missing_count=$((missing_count + 1))
    if [ -z "$missing" ]; then
      missing=$face
    else
      missing="$missing,$face"
    fi
  fi
done

state=healthy
if [ "$missing_count" -gt 0 ]; then
  state=degraded
fi

printf '{"pattern":"M3.simplicial-task-graph","state":"%s","missing_count":%s,"missing":"%s"}\n' \
  "$state" "$missing_count" "$missing" > "$state_root/simplicial-task-graph.json"

[ "$state" = "healthy" ] || exit 75
