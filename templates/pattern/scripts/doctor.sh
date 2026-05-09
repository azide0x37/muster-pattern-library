#!/usr/bin/env sh
set -eu

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
printf '%s\n' "ok: pattern files present"
