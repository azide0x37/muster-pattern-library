#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help) printf '%s\n' "Check T3C1.edge-appliance-bundle artifacts. Use --strict to require systemd-analyze."; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/example.service"
test -f "$pattern_dir/units/muster-appliance.target"
test -f "$pattern_dir/units/muster-recover@.service"
test -x "$pattern_dir/scripts/appliance-doctor.sh"
test -x "$pattern_dir/scripts/muster-recover.sh"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/example.service" "$pattern_dir/units/muster-appliance.target" "$pattern_dir/units/muster-recover@.service"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-t3c1-doctor}
mkdir -p "$mock_root/run/muster"
printf '%s\n' '{"state":"unknown","facts":{}}' > "$mock_root/run/muster/status.json"
MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/appliance-doctor.sh" --once >/dev/null
test -s "$mock_root/run/muster/appliance.json"
printf '%s\n' "ok: T3C1.edge-appliance-bundle"
