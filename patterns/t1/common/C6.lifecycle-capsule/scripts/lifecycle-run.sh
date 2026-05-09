#!/usr/bin/env sh
set -eu

root=${MUSTER_ROOT:-}
project=${PROJECT:-muster-lifecycle-example}
state_dir="$root/var/lib/$project"
mkdir -p "$state_dir"
printf '{"project":"%s","state":"healthy"}\n' "$project" > "$state_dir/lifecycle-run.json"
printf '%s\n' "ok: lifecycle run for $project"
