#!/usr/bin/env sh
set -eu

pattern_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$pattern_dir/manifest.yaml"
test -f "$pattern_dir/README.md"
test -f "$pattern_dir/units/example.service"
printf '%s\n' "ok: T3M3.sheaf-of-services"
