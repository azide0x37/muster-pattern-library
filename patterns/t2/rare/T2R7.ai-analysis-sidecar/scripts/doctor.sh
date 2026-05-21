#!/usr/bin/env sh
set -eu

strict=0
for arg in "$@"; do
  case "$arg" in
    --strict) strict=1 ;;
    -h|--help)
      printf '%s\n' "Check T2R7.ai-analysis-sidecar draft artifacts. Use --strict to require systemd-analyze."
      exit 0
      ;;
    *)
      printf '%s\n' "unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/example.service"
test -f "$pattern_dir/units/example.timer"
test -f "$pattern_dir/examples/minimal/README.md"

if command -v systemd-analyze >/dev/null 2>&1; then
  systemd-analyze verify "$pattern_dir/units/example.service" "$pattern_dir/units/example.timer"
elif [ "$strict" -eq 1 ]; then
  printf '%s\n' "systemd-analyze is required in --strict mode" >&2
  exit 1
else
  printf '%s\n' "warn: systemd-analyze not found; skipped unit verification"
fi

printf '%s\n' "ok: T2R7.ai-analysis-sidecar"
