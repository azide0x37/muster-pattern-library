#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help) printf '%s\n' "Check TR4.device-triggered-conveyor artifacts. Use --strict to require systemd-analyze."; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
repo_root=$(CDPATH= cd -- "$pattern_dir/../../../.." && pwd)
wait_script="$repo_root/patterns/t2/common/TC1.hot-cold-nas-conveyor/scripts/wait-for-hot-capacity.sh"

test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/udev/90-muster-device-conveyor.rules"
test -f "$pattern_dir/units/muster-device-conveyor@.service"
test -f "$pattern_dir/units/muster-device-conveyor-drain.service"
test -f "$pattern_dir/units/muster-device-conveyor-drain.timer"
test -x "$pattern_dir/scripts/device-convey.sh"
test -x "$wait_script"
grep -q 'SYSTEMD_WANTS' "$pattern_dir/udev/90-muster-device-conveyor.rules"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/muster-device-conveyor@.service" "$pattern_dir/units/muster-device-conveyor-drain.service" "$pattern_dir/units/muster-device-conveyor-drain.timer"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-tr4-doctor}
mkdir -p "$mock_root/run/muster"
MUSTER_MOCK_ROOT="$mock_root" WAIT_FOR_HOT_CAPACITY="$wait_script" MUSTER_MOCK_BACKPRESSURE=1 MIN_HOT_FREE_BYTES=1 CAPACITY_TIMEOUT_SECONDS=5 CAPACITY_INTERVAL_SECONDS=1 DRAIN_COMMAND="touch '$mock_root/run/muster/capacity-ready'" "$pattern_dir/scripts/device-convey.sh" /dev/sr0 >/dev/null
test -s "$mock_root/run/muster/device-conveyor.json"
test -s "$mock_root/run/muster/device-conveyor-handoff.json"
printf '%s\n' "ok: TR4.device-triggered-conveyor"
