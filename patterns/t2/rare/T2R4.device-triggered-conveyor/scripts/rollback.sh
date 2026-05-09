#!/usr/bin/env sh
set -eu

apply=0
root=${MUSTER_ROOT:-}
ledger_dir="$root/var/lib/muster/lifecycle/T2R4.device-triggered-conveyor"
backup_dir="$ledger_dir/previous"

usage() {
  printf '%s\n' "Rollback T2R4.device-triggered-conveyor installed artifacts."
  printf '%s\n' "Default mode is dry-run; use --apply to restore previous artifacts."
  printf '%s\n' "Set MUSTER_ROOT for staged-root rollback."
}

for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ] && [ -z "$root" ] && [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "--apply requires root unless MUSTER_ROOT is set." >&2
  exit 1
fi
if [ ! -d "$backup_dir" ]; then
  printf '%s\n' "no previous T2R4.device-triggered-conveyor artifacts recorded" >&2
  exit 1
fi

restore_file() {
  rel=$1
  target="$root/$rel"
  if [ ! -f "$backup_dir/$rel" ]; then
    return 0
  fi
  if [ "$apply" -eq 1 ]; then
    mkdir -p "$(dirname "$target")"
    cp -p "$backup_dir/$rel" "$target"
  else
    printf '%s\n' "dry-run: restore $target"
  fi
}

restore_file "etc/systemd/system/muster-device-conveyor@.service"
restore_file "etc/systemd/system/muster-device-conveyor-drain.service"
restore_file "etc/systemd/system/muster-device-conveyor-drain.timer"
restore_file "etc/udev/rules.d/90-muster-device-conveyor.rules"
restore_file "usr/local/lib/muster/device-convey.sh"
restore_file "usr/local/lib/muster/convey"
restore_file "usr/local/lib/muster/wait-for-hot-capacity.sh"
printf '%s\n' "rollback plan complete for T2R4.device-triggered-conveyor"
