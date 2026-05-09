#!/usr/bin/env sh
set -eu

device=${1:-/dev/mock0}
apply=0
shift || true
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Record a device-bound systemd invocation. Default is dry-run mock mode; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-r2-device-binding}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$state_root"
printf '{"device":"%s","state":"observed","trigger":"udev-systemd"}\n' "$device" > "$state_root/device-binding.json"
printf '%s\n' "ok: device binding recorded for $device"
