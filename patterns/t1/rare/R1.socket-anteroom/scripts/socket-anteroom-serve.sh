#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Emit a bounded local control response for a socket-activated service."
      printf '%s\n' "Default mode uses a mock root; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  root=${MUSTER_ROOT:-}
else
  root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-r1-anteroom}
fi

state_root=${STATE_ROOT:-$root/run/muster}
mkdir -p "$state_root"

request=${SOCKET_ANTEROOM_REQUEST:-ping}
state=healthy
if [ "$request" = "deny" ]; then
  state=degraded
fi

printf '{"pattern":"R1.socket-anteroom","state":"%s","scope":"localhost","request":"%s"}\n' \
  "$state" "$request" > "$state_root/socket-anteroom.json"
printf '{"state":"%s","scope":"localhost"}\n' "$state"
