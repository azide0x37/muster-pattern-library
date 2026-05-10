#!/usr/bin/env sh
set -eu

apply=0
evidence_arg=

usage() {
  printf '%s\n' "Evaluate a local proposition against a concrete evidence path."
  printf '%s\n' "Default mode creates mock evidence; use --apply for real evidence paths."
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) apply=1; shift ;;
    --evidence) evidence_arg=${2:?missing evidence path}; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  root=${MUSTER_ROOT:-}
else
  root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-m4-topos}
fi

state_root=${STATE_ROOT:-$root/run/muster}
mkdir -p "$state_root"

if [ -n "$evidence_arg" ]; then
  evidence=$evidence_arg
else
  evidence=${TOPOS_EVIDENCE:-$root/var/lib/muster/topos/evidence.ready}
fi

if [ "$apply" -ne 1 ] && [ -z "${TOPOS_EVIDENCE:-}" ] && [ -z "$evidence_arg" ]; then
  mkdir -p "$(dirname "$evidence")"
  printf '%s\n' "ready" > "$evidence"
fi

state=failed
truth=false
if [ -e "$evidence" ]; then
  state=healthy
  truth=true
fi

printf '{"pattern":"M4.local-topos-runtime","state":"%s","proposition":"evidence_exists","truth":%s,"evidence":"%s"}\n' \
  "$state" "$truth" "$evidence" > "$state_root/local-topos-runtime.json"

[ "$state" = "healthy" ]
