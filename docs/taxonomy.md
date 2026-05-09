# Muster Taxonomy

Muster classifies patterns by two axes: tech level and rarity.

## Tech Levels

Tech I patterns are atomic operational shapes. They are small enough to understand from one or two systemd unit types plus a narrow script or convention.

Tech II patterns compose Tech I atoms into useful appliance subsystems. They usually have an input, output, failure path, and operator-facing status.

Tech III patterns are local operating doctrines. They coordinate multiple Tech II patterns and make claims about system state, recovery, and intent.

## Rarity

Common patterns should be boring, reusable, and low-surprise.

Rare patterns are practical but more environment-sensitive. They often involve hardware, credentials, sockets, resource constraints, or multi-service state.

Mythic patterns are speculative but still pinned down. They must identify a minimum useful implementation and clearly separate that from the full idea.

## MRL

MRL means Muster Readiness Level.

```text
9  Production-boring and easy to copy safely.
7  Practical with known footguns.
5  Useful in real projects, but environment-sensitive.
3  Researchy or orchestration-heavy.
1  Mostly thesis material.
```

## Pattern IDs

```text
C1   Tech I Common
R1   Tech I Rare
M1   Tech I Mythic
TC1  Tech II Common
TR1  Tech II Rare
TM1  Tech II Mythic
T3C1 Tech III Common
T3R1 Tech III Rare
T3M1 Tech III Mythic
```

Tech III Mythic patterns use `T3M*` to avoid colliding with Tech II Mythic `TM*`.
