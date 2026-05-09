#!/usr/bin/env sh
set -eu

project=${PROJECT:-muster-lifecycle-example}
root=${MUSTER_ROOT:-}
apply=0
purge_state=0
config_dir="$root/etc/$project"
install_dir="$root/opt/$project"
systemd_unit="$root/etc/systemd/system/$project.service"
ledger_dir="$root/var/lib/muster/lifecycle/$project"

usage() {
  printf '%s\n' "Cleanly uninstall C6.lifecycle-capsule artifacts."
  printf '%s\n' "Default mode is dry-run; use --apply to remove owned installed artifacts."
  printf '%s\n' "Config, durable state, and ledgers are preserved unless --purge-state is explicit."
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

remove_path "$systemd_unit"
remove_path "$install_dir"

if [ "$purge_state" -eq 1 ]; then
  remove_path "$config_dir"
  remove_path "$ledger_dir"
else
  printf '%s\n' "preserve config and lifecycle ledger for $project"
fi

printf '%s\n' "uninstall plan complete for C6.lifecycle-capsule"
