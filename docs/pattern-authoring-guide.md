# Pattern Authoring Guide

Use the template in `templates/pattern/` when adding a pattern.

## Required Files

Every pattern folder needs:

```text
README.md
manifest.yaml
units/
scripts/
tests/
examples/
```

Mythic patterns may ship toy units or placeholder scripts, but they still need concrete artifacts and explicit status.

## README Sections

Every README must include:

```text
## Intent
## When to use this
## When not to use this
## System shape
## Subpatterns
## Files
## Installation
## Verification
## Failure modes
## Rollback
## Security notes
## Future work
```

## Choosing MRL

Use high MRL for patterns that are operationally ordinary and easy to verify. Lower the MRL when the pattern depends on flaky hardware, unclear recovery semantics, security-sensitive resources, or speculative orchestration.

## Subpatterns

List actual dependencies in `subpatterns`. List compatible but optional neighbors in `composes_with`.

Do not cite a subpattern unless the pattern contract really depends on it.

## Mythic Discipline

Mythic patterns must say:

- the practical kernel
- the minimum useful implementation
- the full speculative version
- how to de-mythicize the idea
- operational risks

Speculative does not mean vague.
