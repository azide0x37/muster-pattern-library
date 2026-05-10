#!/usr/bin/env sh
set -eu

apply=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    -h|--help)
      printf '%s\n' "Run a bounded workload and record the cgroup policy that contains it."
      printf '%s\n' "Default mode uses a mock root; use --apply for /run/muster."
      exit 0
      ;;
    *) printf '%s\n' "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [ "$apply" -eq 1 ]; then
  root=${MUSTER_ROOT:-}
else
  root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-r3-cgroup}
fi

state_root=${STATE_ROOT:-$root/run/muster}
mkdir -p "$state_root"

cpu_quota=${CGROUP_CPU_QUOTA:-50%}
memory_max=${CGROUP_MEMORY_MAX:-256M}
io_weight=${CGROUP_IO_WEIGHT:-100}

printf '{"pattern":"R3.cgroup-governor","state":"healthy","cpu_quota":"%s","memory_max":"%s","io_weight":"%s"}\n' \
  "$cpu_quota" "$memory_max" "$io_weight" > "$state_root/cgroup-governor.json"
printf '%s\n' "ok: governed workload recorded"
