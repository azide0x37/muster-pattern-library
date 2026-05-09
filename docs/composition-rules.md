# Composition Rules

Composition rules keep the catalog from becoming a loose hierarchy of vibes.

## Rule Table

```yaml
Tech I:
  common: []
  rare: []
  mythic: []

Tech II Common:
  may_use:
    - T1 Common

Tech II Rare:
  may_use:
    - T1 Common
    - T1 Rare
    - T2 Common

  example:
    - TR4.device-triggered-conveyor

Tech II Mythic:
  may_use:
    - T1 Common
    - T1 Rare
    - T1 Mythic
    - T2 Common
    - T2 Rare

Tech III Common:
  may_use:
    - T1 Common
    - T2 Common

Tech III Rare:
  may_use:
    - T1 Common
    - T1 Rare
    - T2 Common
    - T2 Rare
    - T3 Common

Tech III Mythic:
  may_use:
    - T1 Common
    - T1 Rare
    - T1 Mythic
    - T2 Common
    - T2 Rare
    - T2 Mythic
    - T3 Common
    - T3 Rare
```

## Enforcement

`tools/check_composition_rules.py` validates every `subpatterns` entry in each manifest.

Tech I patterns must not declare subpatterns. Tech III Mythic patterns may depend on lower-level patterns and on Tech III Common or Rare patterns, but not on other Tech III Mythic patterns by default.
