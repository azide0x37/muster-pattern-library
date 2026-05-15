#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help) printf '%s\n' "Check C2.persistent-tick artifacts. Use --strict to require systemd-analyze."; exit 0 ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/example.service"
test -f "$pattern_dir/units/example.timer"
test -x "$pattern_dir/scripts/persistent-tick-run.sh"

mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-c2-doctor}
mkdir -p "$mock_root/run/muster" "$mock_root/var/lib/muster/persistent-tick"

if command -v systemd-analyze >/dev/null 2>&1; then
  verify_service="$mock_root/example.service"
  verify_timer="$mock_root/example.timer"
  awk \
    -v readme="$pattern_dir/README.md" \
    -v runner="$pattern_dir/scripts/persistent-tick-run.sh" \
    '
      /^Documentation=/ { print "Documentation=file:" readme; next }
      /^ExecStart=/ { print "ExecStart=" runner " --apply"; next }
      { print }
    ' "$pattern_dir/units/example.service" > "$verify_service"
  awk \
    -v readme="$pattern_dir/README.md" \
    '
      /^Documentation=/ { print "Documentation=file:" readme; next }
      { print }
    ' "$pattern_dir/units/example.timer" > "$verify_timer"
  systemd-analyze verify "$verify_service" "$verify_timer"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

MUSTER_MOCK_ROOT="$mock_root" "$pattern_dir/scripts/persistent-tick-run.sh" >/dev/null
test -d "$mock_root/var/lib/muster/persistent-tick"
test -s "$mock_root/run/muster/persistent-tick.json"
printf '%s\n' "ok: C2.persistent-tick"
