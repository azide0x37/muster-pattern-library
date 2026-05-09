#!/usr/bin/env sh
set -eu

project=${PROJECT:-muster-lifecycle-example}
version=${MUSTER_VERSION:-0.1.0}
root=${MUSTER_ROOT:-}
apply=0

config_dir="$root/etc/$project"
config_file="$config_dir/$project.env"
install_dir="$root/opt/$project"
release_dir="$install_dir/releases/$version"
current_link="$install_dir/current"
systemd_dir="$root/etc/systemd/system"
ledger_dir="$root/var/lib/muster/lifecycle/$project"

usage() {
  printf '%s\n' "Install C6.lifecycle-capsule artifacts."
  printf '%s\n' "Default mode is dry-run; use --apply to copy files."
  printf '%s\n' "Set MUSTER_ROOT to perform a staged-root install without touching the host."
  printf '%s\n' "Set PROJECT and MUSTER_VERSION to choose the install identity."
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

write_config() {
  if [ -f "$config_file" ]; then
    printf '%s\n' "preserve existing config: $config_file"
    return 0
  fi
  if [ "$apply" -eq 1 ]; then
    mkdir -p "$config_dir"
    {
      printf 'PROJECT=%s\n' "$project"
      printf 'VERSION=%s\n' "$version"
    } > "$config_file"
    chmod 0644 "$config_file"
  else
    printf '%s\n' "dry-run: create config $config_file"
  fi
}

switch_current() {
  previous=
  if [ -L "$current_link" ]; then
    previous=$(readlink "$current_link")
  fi
  target="releases/$version"
  if [ "$apply" -eq 1 ]; then
    mkdir -p "$install_dir" "$ledger_dir"
    if [ -n "$previous" ] && [ "$previous" != "$target" ]; then
      printf '%s\n' "$previous" > "$ledger_dir/previous-target"
    fi
    rm -f "$current_link.next"
    ln -s "$target" "$current_link.next"
    rm -f "$current_link"
    mv -f "$current_link.next" "$current_link"
    printf '%s\n' "$target" > "$ledger_dir/current-target"
  else
    printf '%s\n' "dry-run: switch $current_link -> $target"
  fi
}

write_ledger() {
  if [ "$apply" -ne 1 ]; then
    printf '%s\n' "dry-run: write lifecycle ledger $ledger_dir"
    return 0
  fi
  mkdir -p "$ledger_dir"
  {
    printf '%s\n' "$systemd_dir/$project.service"
    printf '%s\n' "$install_dir"
    printf '%s\n' "$current_link"
  } > "$ledger_dir/owned-artifacts.list"
  printf '%s\n' "$version" > "$ledger_dir/version"
}

if [ "$apply" -eq 1 ] && [ -z "$root" ] && [ "$(id -u)" -ne 0 ]; then
  printf '%s\n' "--apply requires root unless MUSTER_ROOT is set." >&2
  exit 1
fi

run install -d -m 0755 "$release_dir/bin" "$release_dir/doc" "$systemd_dir" "$ledger_dir"
run install -m 0755 "$pattern_dir/scripts/lifecycle-run.sh" "$release_dir/bin/lifecycle-run.sh"
run install -m 0644 "$pattern_dir/README.md" "$release_dir/doc/README.md"
run install -m 0644 "$pattern_dir/manifest.yaml" "$release_dir/doc/manifest.yaml"
run install -m 0644 "$pattern_dir/units/example.service" "$systemd_dir/$project.service"
write_config
switch_current
write_ledger

printf '%s\n' "install plan complete for C6.lifecycle-capsule $project $version"
