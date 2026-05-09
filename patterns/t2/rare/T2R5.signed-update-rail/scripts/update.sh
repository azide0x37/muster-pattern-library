#!/usr/bin/env sh
set -eu

project=${PROJECT:-muster-lifecycle-example}
root=${MUSTER_ROOT:-}
manifest_override=
config_file="$root/etc/$project/$project.env"
install_dir="$root/opt/$project"
releases_dir="$install_dir/releases"
current_link="$install_dir/current"
ledger_dir="$root/var/lib/muster/lifecycle/$project"
tmp_dir="${TMPDIR:-/tmp}/muster-update.$$"

usage() {
  printf '%s\n' "Run T2R5.signed-update-rail."
  printf '%s\n' "Use --manifest PATH_OR_URL to override UPDATE_MANIFEST_URL."
  printf '%s\n' "Set MUSTER_ROOT for staged-root update verification."
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --manifest)
      shift
      if [ "$#" -eq 0 ]; then
        printf '%s\n' "--manifest requires a value" >&2
        exit 2
      fi
      manifest_override=$1
      ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT INT TERM

log() {
  printf '%s\n' "$*"
}

json_value() {
  key=$1
  sed -n "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" "$2" | head -n 1
}

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

fetch_to() {
  source=$1
  dest=$2
  case "$source" in
    file://*) cp "${source#file://}" "$dest" ;;
    /*|./*|../*) cp "$source" "$dest" ;;
    *) curl -fsSL "$source" -o "$dest" ;;
  esac
}

if [ -f "$config_file" ]; then
  # shellcheck disable=SC1090
  . "$config_file"
fi

if [ "${AUTOUPDATE:-1}" = "0" ] && [ -z "$manifest_override" ]; then
  log "AUTOUPDATE=0; skipping update"
  exit 0
fi

manifest_url=${manifest_override:-${UPDATE_MANIFEST_URL:-}}
if [ -z "$manifest_url" ] || printf '%s' "$manifest_url" | grep -q '[<>]'; then
  log "UPDATE_MANIFEST_URL is not configured for a real release"
  exit 0
fi

mkdir -p "$tmp_dir" "$releases_dir" "$ledger_dir"
fetch_to "$manifest_url" "$tmp_dir/manifest.json"

new_version=$(json_value version "$tmp_dir/manifest.json")
artifact_url=$(json_value artifact_url "$tmp_dir/manifest.json")
artifact_sha=$(json_value sha256 "$tmp_dir/manifest.json")

if [ -z "$new_version" ] || [ -z "$artifact_url" ] || [ -z "$artifact_sha" ]; then
  log "Manifest missing version, artifact_url, or sha256"
  exit 1
fi

current_version=$(basename "$(readlink "$current_link" 2>/dev/null || echo none)")
if [ "$current_version" = "$new_version" ]; then
  log "$project already at $new_version"
  exit 0
fi

fetch_to "$artifact_url" "$tmp_dir/artifact.tar.gz"
actual_sha=$(sha256_file "$tmp_dir/artifact.tar.gz")
if [ "$actual_sha" != "$artifact_sha" ]; then
  log "SHA256 mismatch for downloaded artifact"
  exit 1
fi

previous_target=$(readlink "$current_link" 2>/dev/null || true)
release_dir="$releases_dir/$new_version"
rm -rf "$release_dir"
mkdir -p "$release_dir"
tar -xzf "$tmp_dir/artifact.tar.gz" -C "$release_dir" --strip-components=1

rm -f "$current_link.next"
ln -s "releases/$new_version" "$current_link.next"
rm -f "$current_link"
mv -f "$current_link.next" "$current_link"
if [ -n "$previous_target" ]; then
  printf '%s\n' "$previous_target" > "$ledger_dir/previous-target"
fi
printf '%s\n' "releases/$new_version" > "$ledger_dir/current-target"

doctor=${DOCTOR_CMD:-$current_link/bin/doctor.sh}
if [ ! -x "$doctor" ]; then
  log "Doctor is missing or not executable: $doctor"
  doctor_failed=1
else
  doctor_failed=0
  MUSTER_ROOT="$root" PROJECT="$project" "$doctor" || doctor_failed=1
fi

if [ "$doctor_failed" -ne 0 ]; then
  log "Health check failed after update; rolling back"
  if [ -n "$previous_target" ]; then
    rm -f "$current_link.next"
    ln -s "$previous_target" "$current_link.next"
    rm -f "$current_link"
    mv -f "$current_link.next" "$current_link"
    printf '%s\n' "$previous_target" > "$ledger_dir/current-target"
  else
    rm -f "$current_link"
  fi
  exit 1
fi

log "Updated $project to $new_version"
