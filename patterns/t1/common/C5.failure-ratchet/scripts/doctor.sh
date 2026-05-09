#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help) printf '%s\n' "Check C5.failure-ratchet artifacts. Use --strict to require systemd-analyze."; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/example.service"
test -f "$pattern_dir/units/muster-recover@.service"
test -x "$pattern_dir/scripts/failure-prone-job.sh"
test -x "$pattern_dir/scripts/muster-recover.sh"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/example.service" "$pattern_dir/units/muster-recover@.service"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-c5-doctor}
mkdir -p "$mock_root/run/muster" "$mock_root/var/lib/muster/recovery"
MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/failure-prone-job.sh" >/dev/null
MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/muster-recover.sh" example.service >/dev/null
test -s "$mock_root/run/muster/recovery.json"
printf '%s\n' "ok: C5.failure-ratchet"
