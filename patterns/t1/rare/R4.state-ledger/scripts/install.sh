#!/usr/bin/env sh
set -eu

apply=0
root=${MUSTER_ROOT:-}

usage() {
  printf '%s\n' "Install R4.state-ledger artifacts."
  printf '%s\n' "Default mode is dry-run; use --apply to copy reviewed artifacts."
  printf '%s\n' "Set MUSTER_ROOT for staged-root installs."
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

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
unit_dir="$root/etc/systemd/system"
lib_dir="$root/usr/local/lib/muster"

run() {
  if [ "$apply" -eq 1 ]; then
    "$@"
  else
    printf 'dry-run:'
    printf ' %s' "$@"
    printf '\n'
  fi
}

run install -d -m 0755 "$unit_dir" "$lib_dir"
run install -m 0644 "$pattern_dir/units/example.service" "$unit_dir/muster-state-ledger.service"
run install -m 0755 "$pattern_dir/scripts/state-ledger-write.sh" "$lib_dir/state-ledger-write.sh"

printf '%s\n' "install plan complete for R4.state-ledger"
