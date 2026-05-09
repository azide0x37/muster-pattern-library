#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help) printf '%s\n' "Check T2C5.local-sidecar-bridge artifacts. Use --strict to require systemd-analyze."; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/muster-sidecar-bridge.service"
test -f "$pattern_dir/units/muster-sidecar-bridge.timer"
test -x "$pattern_dir/scripts/bridge-status.sh"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/muster-sidecar-bridge.service" "$pattern_dir/units/muster-sidecar-bridge.timer"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-tc5-doctor}
mkdir -p "$mock_root/run/muster"
printf '%s\n' '{"state":"unknown"}' > "$mock_root/run/muster/status.json"
MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/bridge-status.sh" --once >/dev/null
test -s "$mock_root/run/muster/sidecar-bridge.json"
printf '%s\n' "ok: T2C5.local-sidecar-bridge"
