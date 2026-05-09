#!/usr/bin/env sh
set -eu

apply=0
root=${MUSTER_ROOT:-}
unit_dir=${UNIT_DIR:-$root/etc/systemd/system}
udev_dir=${UDEV_DIR:-$root/etc/udev/rules.d}
lib_dir=${LIB_DIR:-$root/usr/local/lib/muster}
config_dir=${CONFIG_DIR:-$root/etc/muster}
config_file="$config_dir/device-conveyor.env"
ledger_dir="$root/var/lib/muster/lifecycle/T2R4.device-triggered-conveyor"
backup_dir="$ledger_dir/previous"

usage() {
  printf '%s\n' "Install T2R4.device-triggered-conveyor artifacts for Debian/RPi OS."
  printf '%s\n' "Default mode is dry-run; use --apply to copy files."
  printf '%s\n' "Set MUSTER_ROOT for staged-root installs that do not touch the host."
}

for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
repo_root=$(CDPATH= cd -- "$pattern_dir/../../../.." && pwd)
conveyor_dir="$repo_root/patterns/t2/common/T2C1.hot-cold-nas-conveyor"

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

backup_existing() {
  rel=$1
  target=$2
  if [ "$apply" -eq 1 ] && [ -e "$target" ]; then
    mkdir -p "$backup_dir/$(dirname "$rel")"
    cp -p "$target" "$backup_dir/$rel"
  fi
}

install_file() {
  mode=$1
  source=$2
  target=$3
  rel=$4
  backup_existing "$rel" "$target"
  run install -m "$mode" "$source" "$target"
}

write_config() {
  if [ "$apply" -eq 1 ]; then
    mkdir -p "$config_dir"
    if [ ! -f "$config_file" ]; then
      {
        printf 'CAPABILITY_PATH=/mnt/muster/cold\n'
        printf 'HOT_ROOT=/var/cache/muster/hot\n'
        printf 'BASE_ROOT=/var/lib/muster/device-conveyor\n'
        printf 'STATE_ROOT=/run/muster\n'
      } > "$config_file"
      chmod 0644 "$config_file"
    fi
  else
    printf '%s\n' "dry-run: preserve or create $config_file"
  fi
}

write_ledger() {
  if [ "$apply" -ne 1 ]; then
    printf '%s\n' "dry-run: write lifecycle ledger $ledger_dir"
    return 0
  fi
  mkdir -p "$ledger_dir"
  {
    printf '%s\n' "$unit_dir/muster-device-conveyor@.service"
    printf '%s\n' "$unit_dir/muster-device-conveyor-drain.service"
    printf '%s\n' "$unit_dir/muster-device-conveyor-drain.timer"
    printf '%s\n' "$udev_dir/90-muster-device-conveyor.rules"
    printf '%s\n' "$lib_dir/device-convey.sh"
    printf '%s\n' "$lib_dir/convey"
    printf '%s\n' "$lib_dir/wait-for-hot-capacity.sh"
  } > "$ledger_dir/owned-artifacts.list"
}

test -x "$conveyor_dir/scripts/convey.sh"
test -x "$conveyor_dir/scripts/wait-for-hot-capacity.sh"

run install -d -m 0755 "$unit_dir" "$udev_dir" "$lib_dir" "$config_dir" "$ledger_dir"
install_file 0644 "$pattern_dir/units/muster-device-conveyor@.service" "$unit_dir/muster-device-conveyor@.service" "etc/systemd/system/muster-device-conveyor@.service"
install_file 0644 "$pattern_dir/units/muster-device-conveyor-drain.service" "$unit_dir/muster-device-conveyor-drain.service" "etc/systemd/system/muster-device-conveyor-drain.service"
install_file 0644 "$pattern_dir/units/muster-device-conveyor-drain.timer" "$unit_dir/muster-device-conveyor-drain.timer" "etc/systemd/system/muster-device-conveyor-drain.timer"
install_file 0644 "$pattern_dir/udev/90-muster-device-conveyor.rules" "$udev_dir/90-muster-device-conveyor.rules" "etc/udev/rules.d/90-muster-device-conveyor.rules"
install_file 0755 "$pattern_dir/scripts/device-convey.sh" "$lib_dir/device-convey.sh" "usr/local/lib/muster/device-convey.sh"
install_file 0755 "$conveyor_dir/scripts/convey.sh" "$lib_dir/convey" "usr/local/lib/muster/convey"
install_file 0755 "$conveyor_dir/scripts/wait-for-hot-capacity.sh" "$lib_dir/wait-for-hot-capacity.sh" "usr/local/lib/muster/wait-for-hot-capacity.sh"
write_config
write_ledger
printf '%s\n' "install plan complete for T2R4.device-triggered-conveyor"
