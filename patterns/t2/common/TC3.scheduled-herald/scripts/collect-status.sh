#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Collect Muster health into status.json. Default is dry-run mock mode; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  state_root=${STATE_ROOT:-/run/muster}
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-tc3-herald}
  state_root=${STATE_ROOT:-$mock_root/run/muster}
fi

mkdir -p "$state_root"
status_file="$state_root/status.json"
now=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

cat > "$status_file" <<EOF
{"machine":"muster-edge","role":"edge-appliance","state":"unknown","confidence":0.5,"updated_at":"$now","facts":{"status_source":"scheduled-herald"}}
EOF

test -s "$status_file"
printf '%s\n' "ok: wrote $status_file"
