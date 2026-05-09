# Muster Pattern Graph

Generated from manifest `subpatterns` relationships.

```mermaid
graph TD
  C1["C1.service-capsule<br/>Service Capsule"]
  C2["C2.persistent-tick<br/>Persistent Tick"]
  C3["C3.dropfolder-trigger<br/>Dropfolder Trigger"]
  C4["C4.lazy-resource-gate<br/>Lazy Resource Gate"]
  C5["C5.failure-ratchet<br/>Failure Ratchet"]
  M1["M1.local-truth-sheaf<br/>Local Truth Sheaf"]
  M2["M2.holonomy-detector<br/>Holonomy Detector"]
  M3["M3.simplicial-task-graph<br/>Simplicial Task Graph"]
  M4["M4.local-topos-runtime<br/>Local Topos Runtime"]
  M5["M5.temporal-sheaf<br/>Temporal Sheaf"]
  R1["R1.socket-anteroom<br/>Socket Anteroom"]
  R2["R2.device-binding<br/>Device Binding"]
  R3["R3.cgroup-governor<br/>Cgroup Governor"]
  R4["R4.state-ledger<br/>State Ledger"]
  R5["R5.capability-mount<br/>Capability Mount"]
  T3C1["T3C1.edge-appliance-bundle<br/>Edge Appliance Bundle"]
  T3M1["T3M1.machine-priest<br/>Machine Priest"]
  T3M2["T3M2.ritualized-recovery-loop<br/>Ritualized Recovery Loop"]
  T3M3["T3M3.sheaf-of-services<br/>Sheaf of Services"]
  T3M4["T3M4.holonomic-watchdog<br/>Holonomic Watchdog"]
  T3M5["T3M5.intent-bound-runtime<br/>Intent-Bound Runtime"]
  T3R1["T3R1.multi-resource-orchestrator<br/>Multi-Resource Orchestrator"]
  TC1["TC1.hot-cold-nas-conveyor<br/>Hot/Cold NAS Conveyor"]
  TC2["TC2.dropfolder-spooler<br/>Dropfolder Spooler"]
  TC3["TC3.scheduled-herald<br/>Scheduled Herald"]
  TC4["TC4.self-healing-reconnector<br/>Self-Healing Reconnector"]
  TC5["TC5.local-sidecar-bridge<br/>Local Sidecar Bridge"]
  TR1["TR1.bluetooth-audio-gateway<br/>Bluetooth Audio Gateway"]
  TR2["TR2.lazy-capability-media-bus<br/>Lazy Capability Media Bus"]
  TR3["TR3.edge-control-plane<br/>Edge Control Plane"]
  TR4["TR4.device-triggered-conveyor<br/>Device-Triggered Conveyor"]
  TC1 --> T3C1
  TC3 --> T3C1
  TC4 --> T3C1
  TC5 --> T3C1
  T3C1 --> T3M1
  T3R1 --> T3M1
  M1 --> T3M1
  M5 --> T3M1
  C5 --> T3M2
  TC4 --> T3M2
  R4 --> T3M2
  M2 --> T3M2
  M5 --> T3M2
  M1 --> T3M3
  M3 --> T3M3
  TR3 --> T3M3
  TC3 --> T3M3
  M2 --> T3M4
  TC3 --> T3M4
  TC4 --> T3M4
  R4 --> T3M4
  M4 --> T3M5
  M5 --> T3M5
  TR3 --> T3M5
  R5 --> T3M5
  T3C1 --> T3R1
  TR1 --> T3R1
  TR2 --> T3R1
  TR3 --> T3R1
  R2 --> T3R1
  R4 --> T3R1
  C1 --> TC1
  C2 --> TC1
  C4 --> TC1
  C5 --> TC1
  C1 --> TC2
  C3 --> TC2
  C5 --> TC2
  C1 --> TC3
  C2 --> TC3
  C5 --> TC3
  C1 --> TC4
  C2 --> TC4
  C5 --> TC4
  C1 --> TC5
  C2 --> TC5
  C5 --> TC5
  TC4 --> TR1
  TC5 --> TR1
  R2 --> TR1
  R4 --> TR1
  TC1 --> TR2
  R1 --> TR2
  R3 --> TR2
  R5 --> TR2
  TC2 --> TR3
  TC3 --> TR3
  TC5 --> TR3
  R1 --> TR3
  R2 --> TR3
  R4 --> TR3
  C1 --> TR4
  C2 --> TR4
  C4 --> TR4
  C5 --> TR4
  R2 --> TR4
  R5 --> TR4
  TC1 --> TR4
  TC3 --> TR4
```
