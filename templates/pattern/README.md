# Pattern Name

## Intent

State the smallest useful operational shape this pattern provides.

## When to use this

Use this when the target system needs the stated capability and the dependencies are available.

## When not to use this

Do not use this when the operational overhead is larger than the problem.

## System shape

Describe the services, timers, sockets, mounts, scripts, and runtime files involved.

## Subpatterns

List required subpatterns by ID, or say `None`.

## Files

List the files shipped by this pattern.

## Installation

Explain how to install or adapt the artifacts.

For production-beta patterns, document whether install is dry-run, staged-root, or apply-only.

## Verification

Explain how to prove the pattern is working.

## Failure modes

List predictable failure cases and their signals.

## Rollback

Explain how to disable or remove the pattern safely.

If the pattern claims managed lifecycle behavior, document rollback and artifact-only uninstall commands.

## Security notes

Call out users, credentials, sockets, mounts, and device permissions.

## Future work

Name concrete improvements, not vague ambitions.
