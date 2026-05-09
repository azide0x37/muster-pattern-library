#!/usr/bin/env sh
set -eu

apply=0
once=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    --once) once=1 ;;
    -h|--help)
      printf '%s\n' "Move files from hot storage to cold storage. Default is dry-run mock mode; use --apply for real paths."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  hot_root=${HOT_ROOT:-/var/cache/muster/hot}
  cold_root=${COLD_ROOT:-/mnt/muster/cold}
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-tc1-convey}
  hot_root=${HOT_ROOT:-$mock_root/var/cache/muster/hot}
  cold_root=${COLD_ROOT:-$mock_root/mnt/muster/cold}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$hot_root" "$cold_root" "$state_root"
[ -e "$hot_root/example.payload" ] || printf '%s\n' "mock payload" > "$hot_root/example.payload"

for item in "$hot_root"/*; do
  [ -e "$item" ] || continue
  target="$cold_root/$(basename "$item")"
  if [ "$apply" -eq 1 ]; then
    mv "$item" "$target"
  else
    cp "$item" "$target"
  fi
done

printf '{"state":"healthy","hot_root":"%s","cold_root":"%s","once":%s}\n' "$hot_root" "$cold_root" "$once" > "$state_root/nas-conveyor.json"
printf '%s\n' "ok: hot/cold conveyor wrote $state_root/nas-conveyor.json"
