#!/usr/bin/env sh
set -eu

root=${MUSTER_ROOT:-}
apply=0
purge_state=0
unit_dir="$root/etc/systemd/system"
lib_dir="$root/usr/local/lib/muster/signed-update-rail"
config_file="$root/etc/muster/signed-update.env"
ledger_dir="$root/var/lib/muster/lifecycle/signed-update-rail"

usage() {
  printf '%s\n' "Cleanly uninstall T2R5.signed-update-rail artifacts."
  printf '%s\n' "Default mode is dry-run; use --apply to remove update rail units and scripts."
  printf '%s\n' "Config and ledgers are preserved unless --purge-state is explicit."
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
    rm -rf "$1"
  else
    printf '%s\n' "dry-run: remove $1"
  fi
}

remove_path "$unit_dir/muster-signed-update.service"
remove_path "$unit_dir/muster-signed-update.timer"
remove_path "$lib_dir"

if [ "$purge_state" -eq 1 ]; then
  remove_path "$config_file"
  remove_path "$ledger_dir"
else
  printf '%s\n' "preserve update config and lifecycle ledger"
fi

printf '%s\n' "uninstall plan complete for T2R5.signed-update-rail"
