#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help) printf '%s\n' "Check TC1.hot-cold-nas-conveyor artifacts. Use --strict to require systemd-analyze."; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/muster-nas-conveyor.service"
test -f "$pattern_dir/units/muster-nas-conveyor.timer"
test -x "$pattern_dir/scripts/convey.sh"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/muster-nas-conveyor.service" "$pattern_dir/units/muster-nas-conveyor.timer"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

MUSTER_MOCK_ROOT=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-tc1-doctor} "$pattern_dir/scripts/convey.sh" --once >/dev/null
printf '%s\n' "ok: TC1.hot-cold-nas-conveyor"
