#!/usr/bin/env sh
set -eu

name=${1:-cold-storage}
path=${2:-/mnt/muster/cold}
apply=0
shift 2 || true
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Check that a named capability path is usable. Default is dry-run mock mode; use --apply for real paths."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
  check_path=$path
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-r5-capability}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
  check_path=${MUSTER_MOCK_CAPABILITY_PATH:-$mock_root$path}
  mkdir -p "$check_path"
fi

mkdir -p "$state_root"
state=unknown
reason=unproven

if [ ! -d "$check_path" ]; then
  state=failed
  reason=missing_path
elif [ "$apply" -eq 1 ] && command -v findmnt >/dev/null 2>&1 && ! findmnt "$check_path" >/dev/null 2>&1; then
  state=degraded
  reason=not_a_mountpoint
elif [ -r "$check_path" ] && [ -w "$check_path" ]; then
  state=healthy
  reason=read_write_ok
else
  state=degraded
  reason=permission_denied
fi

printf '{"capability":"%s","path":"%s","state":"%s","reason":"%s"}\n' "$name" "$path" "$state" "$reason" > "$state_root/capability-$name.json"

case "$state" in
  healthy) printf '%s\n' "ok: capability $name is healthy"; exit 0 ;;
  degraded) printf '%s\n' "degraded: capability $name $reason"; exit 75 ;;
  failed) printf '%s\n' "failed: capability $name $reason"; exit 1 ;;
  *) printf '%s\n' "unknown: capability $name"; exit 1 ;;
esac
