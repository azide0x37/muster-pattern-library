#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Reduce local unit facts into one coherent machine-state claim."
      printf '%s\n' "Default mode uses a mock root; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  root=${MUSTER_ROOT:-}
else
  root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-m1-truth}
fi

state_root=${STATE_ROOT:-$root/run/muster}
facts_dir=${LOCAL_TRUTH_FACTS_DIR:-$state_root/local-truth/facts}
mkdir -p "$state_root" "$facts_dir"

found=0
failed=0
degraded=0
unknown=0
for fact in "$facts_dir"/*.json; do
  [ -f "$fact" ] || continue
  found=$((found + 1))
  if grep -q '"state":"failed"' "$fact"; then
    failed=$((failed + 1))
  elif grep -q '"state":"degraded"' "$fact"; then
    degraded=$((degraded + 1))
  elif grep -q '"state":"unknown"' "$fact"; then
    unknown=$((unknown + 1))
  fi
done

if [ "$found" -eq 0 ]; then
  printf '%s\n' '{"unit":"self","state":"healthy"}' > "$facts_dir/self.json"
  found=1
fi

state=healthy
if [ "$failed" -gt 0 ]; then
  state=failed
elif [ "$degraded" -gt 0 ] || [ "$unknown" -gt 0 ]; then
  state=degraded
fi

printf '{"pattern":"M1.local-truth-sheaf","state":"%s","facts":%s,"failed":%s,"degraded":%s,"unknown":%s}\n' \
  "$state" "$found" "$failed" "$degraded" "$unknown" > "$state_root/local-truth-sheaf.json"

[ "$failed" -eq 0 ]
