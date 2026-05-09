# Glossary

Pattern: A reusable operational shape with a manifest, README, artifacts, and validation contract.

Subpattern: A pattern that another pattern composes.

Artifact: A unit file, script, test, example, or other concrete file shipped with a pattern.

Contract: The declared provides/requires/subpatterns/status fields plus the behavior promised by the README.

MRL: Muster Readiness Level, from 1 speculative to 9 boring and ready.

Capability: A resource treated as an owned operational permission, not just a path or daemon.

Appliance: A local system that exposes a useful role, reports state, survives reboot, and has recovery entrypoints.

Ritual: A staged recovery sequence with observe, isolate, reset, validate, and rejoin phases.

Herald: A service that turns local status into operator-facing state.

Ledger: A durable or runtime-local record of facts, decisions, and recovery attempts.

Lifecycle Capsule: A local install, doctor, rollback, and uninstall boundary for one reviewed artifact bundle.

Update Rail: A timer-driven path that verifies a release artifact, stages it, promotes it, and rolls back if the doctor gate fails.
