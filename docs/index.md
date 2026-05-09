# Muster Pattern Index

Generated from `patterns/**/manifest.yaml`.

## Tech 1

### Common

| ID | Pattern | MRL | Subpatterns | Status |
| --- | --- | ---: | --- | --- |
| [`C1.service-capsule`](../patterns/t1/common/C1.service-capsule/) | Service Capsule | 9 | - | usable/reviewed/reviewed |
| [`C2.persistent-tick`](../patterns/t1/common/C2.persistent-tick/) | Persistent Tick | 9 | - | usable/reviewed/reviewed |
| [`C3.dropfolder-trigger`](../patterns/t1/common/C3.dropfolder-trigger/) | Dropfolder Trigger | 8 | - | draft/draft/draft |
| [`C4.lazy-resource-gate`](../patterns/t1/common/C4.lazy-resource-gate/) | Lazy Resource Gate | 8 | - | usable/reviewed/reviewed |
| [`C5.failure-ratchet`](../patterns/t1/common/C5.failure-ratchet/) | Failure Ratchet | 7 | - | usable/reviewed/reviewed |

### Rare

| ID | Pattern | MRL | Subpatterns | Status |
| --- | --- | ---: | --- | --- |
| [`R1.socket-anteroom`](../patterns/t1/rare/R1.socket-anteroom/) | Socket Anteroom | 7 | - | draft/draft/draft |
| [`R2.device-binding`](../patterns/t1/rare/R2.device-binding/) | Device Binding | 6 | - | usable/reviewed/reviewed |
| [`R3.cgroup-governor`](../patterns/t1/rare/R3.cgroup-governor/) | Cgroup Governor | 6 | - | draft/draft/draft |
| [`R4.state-ledger`](../patterns/t1/rare/R4.state-ledger/) | State Ledger | 6 | - | draft/draft/draft |
| [`R5.capability-mount`](../patterns/t1/rare/R5.capability-mount/) | Capability Mount | 5 | - | usable/reviewed/reviewed |

### Mythic

| ID | Pattern | MRL | Subpatterns | Status |
| --- | --- | ---: | --- | --- |
| [`M1.local-truth-sheaf`](../patterns/t1/mythic/M1.local-truth-sheaf/) | Local Truth Sheaf | 4 | - | draft/draft/draft |
| [`M2.holonomy-detector`](../patterns/t1/mythic/M2.holonomy-detector/) | Holonomy Detector | 4 | - | draft/draft/draft |
| [`M3.simplicial-task-graph`](../patterns/t1/mythic/M3.simplicial-task-graph/) | Simplicial Task Graph | 3 | - | draft/draft/draft |
| [`M4.local-topos-runtime`](../patterns/t1/mythic/M4.local-topos-runtime/) | Local Topos Runtime | 2 | - | draft/draft/draft |
| [`M5.temporal-sheaf`](../patterns/t1/mythic/M5.temporal-sheaf/) | Temporal Sheaf | 3 | - | draft/draft/draft |

## Tech 2

### Common

| ID | Pattern | MRL | Subpatterns | Status |
| --- | --- | ---: | --- | --- |
| [`TC1.hot-cold-nas-conveyor`](../patterns/t2/common/TC1.hot-cold-nas-conveyor/) | Hot/Cold NAS Conveyor | 8 | C1.service-capsule, C2.persistent-tick, C4.lazy-resource-gate, C5.failure-ratchet | usable/reviewed/reviewed |
| [`TC2.dropfolder-spooler`](../patterns/t2/common/TC2.dropfolder-spooler/) | Dropfolder Spooler | 8 | C1.service-capsule, C3.dropfolder-trigger, C5.failure-ratchet | draft/draft/draft |
| [`TC3.scheduled-herald`](../patterns/t2/common/TC3.scheduled-herald/) | Scheduled Herald | 8 | C1.service-capsule, C2.persistent-tick, C5.failure-ratchet | usable/reviewed/reviewed |
| [`TC4.self-healing-reconnector`](../patterns/t2/common/TC4.self-healing-reconnector/) | Self-Healing Reconnector | 7 | C1.service-capsule, C2.persistent-tick, C5.failure-ratchet | usable/reviewed/reviewed |
| [`TC5.local-sidecar-bridge`](../patterns/t2/common/TC5.local-sidecar-bridge/) | Local Sidecar Bridge | 7 | C1.service-capsule, C2.persistent-tick, C5.failure-ratchet | usable/reviewed/reviewed |

### Rare

| ID | Pattern | MRL | Subpatterns | Status |
| --- | --- | ---: | --- | --- |
| [`TR1.bluetooth-audio-gateway`](../patterns/t2/rare/TR1.bluetooth-audio-gateway/) | Bluetooth Audio Gateway | 6 | TC4.self-healing-reconnector, TC5.local-sidecar-bridge, R2.device-binding, R4.state-ledger | draft/draft/draft |
| [`TR2.lazy-capability-media-bus`](../patterns/t2/rare/TR2.lazy-capability-media-bus/) | Lazy Capability Media Bus | 5 | TC1.hot-cold-nas-conveyor, R1.socket-anteroom, R3.cgroup-governor, R5.capability-mount | draft/draft/draft |
| [`TR3.edge-control-plane`](../patterns/t2/rare/TR3.edge-control-plane/) | Edge Control Plane | 5 | TC2.dropfolder-spooler, TC3.scheduled-herald, TC5.local-sidecar-bridge, R1.socket-anteroom, R2.device-binding, R4.state-ledger | draft/draft/draft |
| [`TR4.device-triggered-conveyor`](../patterns/t2/rare/TR4.device-triggered-conveyor/) | Device-Triggered Conveyor | 5 | C1.service-capsule, C2.persistent-tick, C4.lazy-resource-gate, C5.failure-ratchet, R2.device-binding, R5.capability-mount, TC1.hot-cold-nas-conveyor, TC3.scheduled-herald | usable/reviewed/reviewed |

## Tech 3

### Common

| ID | Pattern | MRL | Subpatterns | Status |
| --- | --- | ---: | --- | --- |
| [`T3C1.edge-appliance-bundle`](../patterns/t3/common/T3C1.edge-appliance-bundle/) | Edge Appliance Bundle | 7 | TC1.hot-cold-nas-conveyor, TC3.scheduled-herald, TC4.self-healing-reconnector, TC5.local-sidecar-bridge | usable/reviewed/reviewed |

### Rare

| ID | Pattern | MRL | Subpatterns | Status |
| --- | --- | ---: | --- | --- |
| [`T3R1.multi-resource-orchestrator`](../patterns/t3/rare/T3R1.multi-resource-orchestrator/) | Multi-Resource Orchestrator | 5 | T3C1.edge-appliance-bundle, TR1.bluetooth-audio-gateway, TR2.lazy-capability-media-bus, TR3.edge-control-plane, R2.device-binding, R4.state-ledger | draft/draft/draft |

### Mythic

| ID | Pattern | MRL | Subpatterns | Status |
| --- | --- | ---: | --- | --- |
| [`T3M1.machine-priest`](../patterns/t3/mythic/T3M1.machine-priest/) | Machine Priest | 3 | T3C1.edge-appliance-bundle, T3R1.multi-resource-orchestrator, M1.local-truth-sheaf, M5.temporal-sheaf | draft/draft/draft |
| [`T3M2.ritualized-recovery-loop`](../patterns/t3/mythic/T3M2.ritualized-recovery-loop/) | Ritualized Recovery Loop | 4 | C5.failure-ratchet, TC4.self-healing-reconnector, R4.state-ledger, M2.holonomy-detector, M5.temporal-sheaf | draft/draft/draft |
| [`T3M3.sheaf-of-services`](../patterns/t3/mythic/T3M3.sheaf-of-services/) | Sheaf of Services | 2 | M1.local-truth-sheaf, M3.simplicial-task-graph, TR3.edge-control-plane, TC3.scheduled-herald | draft/draft/draft |
| [`T3M4.holonomic-watchdog`](../patterns/t3/mythic/T3M4.holonomic-watchdog/) | Holonomic Watchdog | 3 | M2.holonomy-detector, TC3.scheduled-herald, TC4.self-healing-reconnector, R4.state-ledger | draft/draft/draft |
| [`T3M5.intent-bound-runtime`](../patterns/t3/mythic/T3M5.intent-bound-runtime/) | Intent-Bound Runtime | 2 | M4.local-topos-runtime, M5.temporal-sheaf, TR3.edge-control-plane, R5.capability-mount | draft/draft/draft |
