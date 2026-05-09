#!/usr/bin/env sh
set -eu

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/muster-signed-update.service"
test -f "$pattern_dir/units/muster-signed-update.timer"
test -x "$pattern_dir/scripts/update.sh"
test -x "$pattern_dir/scripts/install.sh"
test -x "$pattern_dir/scripts/rollback.sh"
test -x "$pattern_dir/scripts/uninstall.sh"

mock_root=$(mktemp -d "${TMPDIR:-/tmp}/muster-t2r5-doctor.XXXXXX")
cleanup() {
  rm -rf "$mock_root"
}
trap cleanup EXIT INT TERM

project=muster-lifecycle-example
current="$mock_root/opt/$project/current"
mkdir -p "$mock_root/opt/$project/releases/0.1.0/bin"
printf '#!/usr/bin/env sh\nexit 0\n' > "$mock_root/opt/$project/releases/0.1.0/bin/doctor.sh"
chmod 0755 "$mock_root/opt/$project/releases/0.1.0/bin/doctor.sh"
ln -s "releases/0.1.0" "$current"

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

make_artifact() {
  version=$1
  exit_code=$2
  package_dir="$mock_root/pkg-$version/muster-lifecycle-example-$version"
  mkdir -p "$package_dir/bin"
  printf '#!/usr/bin/env sh\nexit %s\n' "$exit_code" > "$package_dir/bin/doctor.sh"
  chmod 0755 "$package_dir/bin/doctor.sh"
  tar -czf "$mock_root/artifact-$version.tar.gz" -C "$mock_root/pkg-$version" "muster-lifecycle-example-$version"
  sha=$(sha256_file "$mock_root/artifact-$version.tar.gz")
  {
    printf '{\n'
    printf '  "version": "%s",\n' "$version"
    printf '  "artifact_url": "%s",\n' "$mock_root/artifact-$version.tar.gz"
    printf '  "sha256": "%s"\n' "$sha"
    printf '}\n'
  } > "$mock_root/manifest-$version.json"
}

make_artifact 0.2.0 0
MUSTER_ROOT="$mock_root" PROJECT="$project" "$pattern_dir/scripts/update.sh" --manifest "$mock_root/manifest-0.2.0.json" >/dev/null
test "$(readlink "$current")" = "releases/0.2.0"

make_artifact 0.3.0 1
if MUSTER_ROOT="$mock_root" PROJECT="$project" "$pattern_dir/scripts/update.sh" --manifest "$mock_root/manifest-0.3.0.json" >/dev/null 2>&1; then
  printf '%s\n' "failing doctor update unexpectedly succeeded" >&2
  exit 1
fi
test "$(readlink "$current")" = "releases/0.2.0"

printf '%s\n' "ok: T2R5.signed-update-rail"
