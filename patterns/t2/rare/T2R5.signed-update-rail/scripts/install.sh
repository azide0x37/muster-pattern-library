#!/usr/bin/env sh
set -eu

root=${MUSTER_ROOT:-}
apply=0
unit_dir="$root/etc/systemd/system"
lib_dir="$root/usr/local/lib/muster/signed-update-rail"
config_dir="$root/etc/muster"
config_file="$config_dir/signed-update.env"

usage() {
  printf '%s\n' "Install T2R5.signed-update-rail artifacts."
  printf '%s\n' "Default mode is dry-run; use --apply to copy files."
  printf '%s\n' "Set MUSTER_ROOT to perform a staged-root install without touching the host."
}

for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

run() {
  if [ "$apply" -eq 1 ]; then
    "$@"
  else
    printf 'dry-run:'
    printf ' %s' "$@"
    printf '\n'
  fi
}

if [ "$apply" -eq 1 ] && [ -z "$root" ] && [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "--apply requires root unless MUSTER_ROOT is set." >&2
  exit 1
fi

run install -d -m 0755 "$unit_dir" "$lib_dir" "$config_dir"
run install -m 0644 "$pattern_dir/units/muster-signed-update.service" "$unit_dir/muster-signed-update.service"
run install -m 0644 "$pattern_dir/units/muster-signed-update.timer" "$unit_dir/muster-signed-update.timer"
run install -m 0755 "$pattern_dir/scripts/update.sh" "$lib_dir/update.sh"
run install -m 0755 "$pattern_dir/scripts/rollback.sh" "$lib_dir/rollback.sh"
run install -m 0755 "$pattern_dir/scripts/uninstall.sh" "$lib_dir/uninstall.sh"

if [ "$apply" -eq 1 ]; then
  if [ ! -f "$config_file" ]; then
    {
      printf 'PROJECT=muster-lifecycle-example\n'
      printf 'AUTOUPDATE=0\n'
      printf 'UPDATE_MANIFEST_URL=\n'
    } > "$config_file"
    chmod 0644 "$config_file"
  fi
else
  printf '%s\n' "dry-run: preserve or create $config_file"
fi

printf '%s\n' "install plan complete for T2R5.signed-update-rail"
