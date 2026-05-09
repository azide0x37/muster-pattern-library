#!/usr/bin/env sh
set -eu

apply=0
unit_dir=${UNIT_DIR:-/etc/systemd/system}
lib_dir=${LIB_DIR:-/usr/local/lib/muster}
config_dir=${CONFIG_DIR:-/etc/muster}

usage() {
  printf '%s\n' "Install C1.service-capsule artifacts for Debian/RPi OS."
  printf '%s\n' "Default mode is dry-run; use --apply to copy files."
  printf '%s\n' "Overrides: UNIT_DIR=$unit_dir LIB_DIR=$lib_dir CONFIG_DIR=$config_dir"
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
run install -m 0644 "$pattern_dir/units/example.service" "$unit_dir/muster-service-capsule.service"
run install -m 0755 "$pattern_dir/scripts/service-capsule-run.sh" "$lib_dir/service-capsule-run.sh"
printf '%s\n' "install plan complete for C1.service-capsule"
