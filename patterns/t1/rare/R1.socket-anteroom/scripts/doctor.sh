#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help) printf '%s\n' "Check R1.socket-anteroom artifacts. Use --strict to require systemd-analyze."; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/example.service"
test -f "$pattern_dir/units/muster-anteroom.socket"
test -f "$pattern_dir/units/muster-anteroom.service"
test -x "$pattern_dir/scripts/socket-anteroom-serve.sh"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/muster-anteroom.socket" "$pattern_dir/units/muster-anteroom.service" "$pattern_dir/units/example.service"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

mock_root=$(mktemp -d "${TMPDIR:-/tmp}/muster-r1-doctor.XXXXXX")
cleanup() {
  rm -rf "$mock_root"
}
trap cleanup EXIT INT TERM

MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/socket-anteroom-serve.sh" >/dev/null
test -s "$mock_root/run/muster/socket-anteroom.json"
printf '%s\n' "ok: R1.socket-anteroom"
