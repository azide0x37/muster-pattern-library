#!/usr/bin/env sh
set -eu

apply=0
once=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    --once) once=1 ;;
    -h|--help)
      printf '%s\n' "Bridge status.json to a local sidecar payload. Default is dry-run mock mode; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-tc5-bridge}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$state_root"
status_file="$state_root/status.json"
bridge_file="$state_root/sidecar-bridge.json"
[ -s "$status_file" ] || printf '%s\n' '{"state":"unknown","facts":{}}' > "$status_file"

printf '{"state":"healthy","source":"%s","destination":"local-file","once":%s}\n' "$status_file" "$once" > "$bridge_file"
printf '%s\n' "ok: wrote $bridge_file"
