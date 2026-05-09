#!/usr/bin/env sh
set -eu

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/example.service"
test -x "$pattern_dir/scripts/install.sh"
test -x "$pattern_dir/scripts/rollback.sh"
test -x "$pattern_dir/scripts/uninstall.sh"
test -x "$pattern_dir/scripts/lifecycle-run.sh"

mock_root=$(mktemp -d "${TMPDIR:-/tmp}/muster-c6-doctor.XXXXXX")
cleanup() {
  rm -rf "$mock_root"
}
trap cleanup EXIT INT TERM

project=muster-lifecycle-example
config="$mock_root/etc/$project/$project.env"
current="$mock_root/opt/$project/current"

MUSTER_ROOT="$mock_root" PROJECT="$project" MUSTER_VERSION=0.1.0 "$pattern_dir/scripts/install.sh" --apply >/dev/null
test -f "$config"
printf '\nUSER_SETTING=kept\n' >> "$config"
MUSTER_ROOT="$mock_root" PROJECT="$project" MUSTER_VERSION=0.1.0 "$pattern_dir/scripts/install.sh" --apply >/dev/null
grep -q "USER_SETTING=kept" "$config"
test "$(readlink "$current")" = "releases/0.1.0"

MUSTER_ROOT="$mock_root" PROJECT="$project" MUSTER_VERSION=0.2.0 "$pattern_dir/scripts/install.sh" --apply >/dev/null
test "$(readlink "$current")" = "releases/0.2.0"
MUSTER_ROOT="$mock_root" PROJECT="$project" "$pattern_dir/scripts/rollback.sh" --apply >/dev/null
test "$(readlink "$current")" = "releases/0.1.0"

MUSTER_ROOT="$mock_root" PROJECT="$project" "$pattern_dir/scripts/uninstall.sh" --apply >/dev/null
test ! -e "$mock_root/opt/$project"
test -f "$config"
test -d "$mock_root/var/lib/muster/lifecycle/$project"

printf '%s\n' "ok: C6.lifecycle-capsule"
