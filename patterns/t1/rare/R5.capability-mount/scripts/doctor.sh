#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help) printf '%s\n' "Check R5.capability-mount artifacts. Use --strict to require systemd-analyze."; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/muster-capability@.service"
test -x "$pattern_dir/scripts/check-capability.sh"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/muster-capability@.service"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-r5-doctor}
MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/check-capability.sh" cold-storage /mnt/muster/cold >/dev/null
test -s "$mock_root/run/muster/capability-cold-storage.json"
printf '%s\n' "ok: R5.capability-mount"
