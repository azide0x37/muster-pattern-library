#!/usr/bin/env sh
set -eu

apply=0
purge_state=0
root=${MUSTER_ROOT:-}
unit_dir=${UNIT_DIR:-$root/etc/systemd/system}
udev_dir=${UDEV_DIR:-$root/etc/udev/rules.d}
lib_dir=${LIB_DIR:-$root/usr/local/lib/muster}
config_file=${CONFIG_FILE:-$root/etc/muster/device-binding.env}
ledger_dir="$root/var/lib/muster/lifecycle/R2.device-binding"

usage() {
  printf '%s\n' "Cleanly uninstall R2.device-binding artifacts."
  printf '%s\n' "Default mode is dry-run; use --apply to remove owned artifacts."
  printf '%s\n' "Config, state, and ledger are preserved unless --purge-state is explicit."
}

for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    --purge-state) purge_state=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ] && [ -z "$root" ] && [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "--apply requires root unless MUSTER_ROOT is set." >&2
  exit 1
fi

remove_path() {
  if [ "$apply" -eq 1 ]; then
    rm -f "$1"
  else
    printf '%s\n' "dry-run: remove $1"
  fi
}

remove_path "$unit_dir/muster-device-bound@.service"
remove_path "$udev_dir/90-muster-device-binding.rules"
remove_path "$lib_dir/device-bound-run.sh"

if [ "$purge_state" -eq 1 ]; then
  if [ "$apply" -eq 1 ]; then
    rm -f "$config_file"
    rm -rf "$ledger_dir"
  else
    printf '%s\n' "dry-run: purge $config_file"
    printf '%s\n' "dry-run: purge $ledger_dir"
  fi
else
  printf '%s\n' "preserve config and lifecycle ledger for R2.device-binding"
fi

printf '%s\n' "uninstall plan complete for R2.device-binding"
