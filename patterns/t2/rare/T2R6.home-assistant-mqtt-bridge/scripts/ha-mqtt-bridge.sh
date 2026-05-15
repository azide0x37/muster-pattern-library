#!/usr/bin/env sh
set -eu

apply=0
discover=0
once=0
control=0
state_entity=
state_value=

usage() {
  printf '%s\n' "Bridge local appliance state to Home Assistant MQTT payloads."
  printf '%s\n' "Default mode is mock filesystem MQTT; use --apply for runtime paths."
  printf '%s\n' "Modes: --discover, --state ENTITY STATE, --control, --once."
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) apply=1; shift ;;
    --discover) discover=1; shift ;;
    --once) once=1; shift ;;
    --control) control=1; shift ;;
    --state)
      shift
      if [ "$#" -lt 2 ]; then
        printf '%s\n' "--state requires ENTITY and STATE" >&2
        exit 2
      fi
      state_entity=$1
      state_value=$2
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) printf '%s\n' "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ "$discover" -eq 0 ] && [ "$once" -eq 0 ] && [ "$control" -eq 0 ] && [ -z "$state_entity" ]; then
  once=1
fi

root=${MUSTER_ROOT:-}
if [ "$apply" -eq 1 ]; then
  base_root=$root
else
  mock_root=${MUSTER_MOCK_ROOT:-${TMPDIR:-/tmp}/muster-ha-mqtt-bridge}
  base_root=$mock_root
fi

state_dir=${STATE_DIR:-$base_root/run/muster/home-assistant-mqtt-bridge}
outbox_dir=${MQTT_OUTBOX_DIR:-$state_dir/mqtt-outbox}
control_dir=${MQTT_CONTROL_DIR:-$state_dir/mqtt-control}
ledger_dir=${LEDGER_DIR:-$base_root/var/lib/muster/home-assistant-mqtt-bridge}
node_id=${HA_NODE_ID:-muster_bridge}
device_name=${HA_DEVICE_NAME:-Muster Home Assistant MQTT Bridge}
discovery_prefix=${HA_DISCOVERY_PREFIX:-homeassistant}
base_topic=${MQTT_BASE_TOPIC:-muster/home-assistant-mqtt-bridge}
state_file="$state_dir/state.json"

mkdir -p "$state_dir" "$outbox_dir" "$control_dir" "$ledger_dir"

validate_token() {
  case "$1" in
    ""|*[!A-Za-z0-9_.:-]*)
      printf '%s\n' "invalid token: $1" >&2
      exit 2
      ;;
  esac
}

topic_file() {
  printf '%s' "$1" | tr '/+' '__'
}

publish() {
  topic=$1
  payload=$2
  file="$outbox_dir/$(topic_file "$topic").json"
  printf '%s\n' "$payload" > "$file"
  printf '%s\t%s\n' "$topic" "$file" >> "$outbox_dir/topics.log"
}

publish_discovery() {
  discovery_topic="$discovery_prefix/device/$node_id/config"
  availability_topic="$base_topic/availability"
  state_topic="$base_topic/state"
  enabled_state_topic="$base_topic/enabled/state"
  enabled_command_topic="$base_topic/cmd/enabled/set"
  restart_command_topic="$base_topic/cmd/restart"
  payload=$(printf '{"device":{"identifiers":["%s"],"name":"%s"},"origin":{"name":"Muster Home Assistant MQTT Bridge","sw_version":"1"},"availability":{"topic":"%s"},"components":{"health":{"platform":"sensor","name":"Health","unique_id":"%s_health","state_topic":"%s","value_template":"{{ value_json.health }}"},"rip_state":{"platform":"sensor","name":"Rip State","unique_id":"%s_rip_state","state_topic":"%s","value_template":"{{ value_json.rip_state }}"},"conveyance_status":{"platform":"sensor","name":"Conveyance Status","unique_id":"%s_conveyance_status","state_topic":"%s","value_template":"{{ value_json.conveyance_status }}"},"restart_service":{"platform":"button","name":"Restart Service","unique_id":"%s_restart_service","command_topic":"%s","payload_press":"PRESS"},"enabled":{"platform":"switch","name":"Enabled","unique_id":"%s_enabled","state_topic":"%s","command_topic":"%s","payload_on":"ON","payload_off":"OFF"}}}' "$node_id" "$device_name" "$availability_topic" "$node_id" "$state_topic" "$node_id" "$state_topic" "$node_id" "$state_topic" "$node_id" "$restart_command_topic" "$node_id" "$enabled_state_topic" "$enabled_command_topic")
  publish "$discovery_topic" "$payload"
  printf '%s\n' "$discovery_topic" > "$ledger_dir/discovery-topic"
}

publish_state() {
  entity=$1
  value=$2
  validate_token "$entity"
  validate_token "$value"
  topic="$base_topic/$entity/state"
  if [ -f "$state_file" ]; then
    cp "$state_file" "$ledger_dir/last-state.json"
    printf '%s\n' "$topic" > "$ledger_dir/last-topic"
  fi
  payload=$(printf '{"entity":"%s","state":"%s","state_topic":"%s","source":"mockable-mqtt"}' "$entity" "$value" "$topic")
  printf '%s\n' "$payload" > "$state_file"
  publish "$topic" "$payload"
}

process_control() {
  found=0
  for command_file in "$control_dir"/*.cmd; do
    [ -e "$command_file" ] || continue
    found=1
    entity=$(basename "$command_file" .cmd)
    command=$(sed -n '1p' "$command_file" | tr -d '\r\n')
    validate_token "$entity"
    case "$entity:$command" in
      enabled:ON|enabled:OFF)
        publish_state "$entity" "$command"
        printf '{"control":"enabled","state":"%s","result":"accepted"}\n' "$command" > "$state_dir/control-result.json"
        publish "$base_topic/control/result" "$(cat "$state_dir/control-result.json")"
        ;;
      restart:PRESS|restart:RESTART)
        printf '{"control":"restart","result":"accepted","action":"restart_service"}\n' > "$state_dir/control-result.json"
        publish "$base_topic/control/result" "$(cat "$state_dir/control-result.json")"
        ;;
      *)
        printf '%s\n' "rejected command for $entity: $command" >&2
        mv "$command_file" "$command_file.rejected"
        exit 1
        ;;
    esac
    mv "$command_file" "$command_file.processed"
  done
  if [ "$found" -eq 0 ]; then
    printf '%s\n' "ok: no pending control commands"
  fi
}

if [ "$discover" -eq 1 ] || [ "$once" -eq 1 ]; then
  publish_discovery
fi

if [ "$once" -eq 1 ] && [ ! -f "$state_file" ]; then
  publish_state relay OFF
fi

if [ -n "$state_entity" ]; then
  publish_state "$state_entity" "$state_value"
fi

if [ "$control" -eq 1 ] || [ "$once" -eq 1 ]; then
  process_control
fi

printf '%s\n' "ok: Home Assistant MQTT bridge wrote $outbox_dir"
