#!/usr/bin/env sh
set -eu

apply=0
unit_dir=${UNIT_DIR:-/etc/systemd/system}
lib_dir=${LIB_DIR:-/usr/local/lib/muster}
config_dir=${CONFIG_DIR:-/etc/muster}

usage() {
  printf '%s\n' "Install TC1.hot-cold-nas-conveyor artifacts for Debian/RPi OS."
  printf '%s\n' "Default mode is dry-run; use --apply to copy files."
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

if [ "$apply" -eq 1 ] && [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "--apply requires root because it writes system locations." >&2
  exit 1
fi

run install -d -m 0755 "$unit_dir" "$lib_dir" "$config_dir"
run install -m 0644 "$pattern_dir/units/muster-nas-conveyor.service" "$unit_dir/muster-nas-conveyor.service"
run install -m 0644 "$pattern_dir/units/muster-nas-conveyor.timer" "$unit_dir/muster-nas-conveyor.timer"
run install -m 0755 "$pattern_dir/scripts/convey.sh" "$lib_dir/convey"
printf '%s\n' "install plan complete for TC1.hot-cold-nas-conveyor"
