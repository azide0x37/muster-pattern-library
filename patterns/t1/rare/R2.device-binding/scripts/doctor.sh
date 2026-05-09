#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help) printf '%s\n' "Check R2.device-binding artifacts. Use --strict to require systemd-analyze."; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/muster-device-bound@.service"
test -f "$pattern_dir/udev/90-muster-device-binding.rules"
test -x "$pattern_dir/scripts/device-bound-run.sh"
grep -q 'SYSTEMD_WANTS' "$pattern_dir/udev/90-muster-device-binding.rules"
if grep -q 'RUN+=' "$pattern_dir/udev/90-muster-device-binding.rules"; then
  printf '%s\n' "udev rule must not run long work directly with RUN+=" >&2
  exit 1
fi
grep -q 'BindsTo=dev-%i.device' "$pattern_dir/units/muster-device-bound@.service"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/muster-device-bound@.service"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-r2-doctor}
MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/device-bound-run.sh" /dev/mock0 >/dev/null
test -s "$mock_root/run/muster/device-binding.json"
printf '%s\n' "ok: R2.device-binding"
