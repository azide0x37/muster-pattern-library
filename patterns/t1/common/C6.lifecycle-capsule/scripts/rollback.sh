#!/usr/bin/env sh
set -eu

project=${PROJECT:-muster-lifecycle-example}
root=${MUSTER_ROOT:-}
apply=0
install_dir="$root/opt/$project"
current_link="$install_dir/current"
ledger_dir="$root/var/lib/muster/lifecycle/$project"
previous_file="$ledger_dir/previous-target"

usage() {
  printf '%s\n' "Rollback C6.lifecycle-capsule to the previous release target."
  printf '%s\n' "Default mode is dry-run; use --apply to switch current."
  printf '%s\n' "Set MUSTER_ROOT for staged-root rollback."
}

for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ ! -f "$previous_file" ]; then
  printf '%s\n' "no previous lifecycle target recorded: $previous_file" >&2
  exit 1
fi

previous=$(cat "$previous_file")
if [ "$apply" -eq 1 ] && [ -z "$root" ] && [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "--apply requires root unless MUSTER_ROOT is set." >&2
  exit 1
fi

if [ "$apply" -eq 1 ]; then
  rm -f "$current_link.next"
  ln -s "$previous" "$current_link.next"
  rm -f "$current_link"
  mv -f "$current_link.next" "$current_link"
  printf '%s\n' "$previous" > "$ledger_dir/current-target"
else
  printf '%s\n' "dry-run: switch $current_link -> $previous"
fi

printf '%s\n' "rollback plan complete for C6.lifecycle-capsule"
