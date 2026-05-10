#!/usr/bin/env sh
set -eu

apply=0
once=0

usage() {
  printf '%s\n' "Process files from a Muster dropfolder inbox."
  printf '%s\n' "Default mode uses a mock root; use --apply for /var/lib/muster and /run/muster."
}

for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    --once) once=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  root=${MUSTER_ROOT:-}
else
  root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-c3-dropfolder}
fi

state_root=${STATE_ROOT:-$root/run/muster}
drop_root=${DROPFOLDER_ROOT:-$root/var/lib/muster/dropfolder}
inbox=${DROPFOLDER_INBOX:-$drop_root/inbox}
work=${DROPFOLDER_WORK:-$drop_root/work}
done_dir=${DROPFOLDER_DONE:-$drop_root/done}
failed_dir=${DROPFOLDER_FAILED:-$drop_root/failed}

mkdir -p "$state_root" "$inbox" "$work" "$done_dir" "$failed_dir"

processed=0
failed=0
for src in "$inbox"/*; do
  [ -e "$src" ] || continue
  [ -f "$src" ] || continue
  base=$(basename "$src")
  claim="$work/$base.processing"
  if mv "$src" "$claim"; then
    if [ "${DROPFOLDER_FORCE_FAIL:-0}" = "1" ]; then
      mv "$claim" "$failed_dir/$base"
      failed=$((failed + 1))
    else
      cp "$claim" "$done_dir/$base"
      rm -f "$claim"
      processed=$((processed + 1))
    fi
  fi
done

state=healthy
if [ "$failed" -gt 0 ]; then
  state=failed
elif [ "$processed" -eq 0 ]; then
  state=unknown
fi

printf '{"pattern":"C3.dropfolder-trigger","state":"%s","processed":%s,"failed":%s,"once":%s}\n' \
  "$state" "$processed" "$failed" "$once" > "$state_root/dropfolder-trigger.json"

[ "$failed" -eq 0 ]
