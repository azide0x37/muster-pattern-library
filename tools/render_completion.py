from __future__ import annotations

import argparse

from completion import (
    DEVICE_TRIGGERED_CONVEYOR_CHAIN,
    FLAGSHIP_CHAIN,
    LIFECYCLE_CHAIN,
    STABLE_DEVICE_CONVEYOR_CHAIN,
    completion_rows,
    grouped_percentages,
    overall_percent,
)
from patternlib import ROOT, validate_all


OUT = ROOT / "docs" / "completion.md"


def render() -> str:
    patterns = validate_all()
    groups = grouped_percentages(patterns)
    rows = completion_rows(patterns)

    lines = [
        "# Muster Completion Report",
        "",
        "Generated from manifest `status` fields.",
        "",
        f"Overall maturity: **{overall_percent(patterns)}%**",
        "",
        "## Group Summary",
        "",
        "| Group | Patterns | Completion |",
        "| --- | ---: | ---: |",
    ]
    for tech_level in [1, 2, 3]:
        for rarity in ["common", "rare", "mythic"]:
            key = (tech_level, rarity)
            if key not in groups:
                continue
            count = sum(1 for pattern in patterns if pattern.tech_level == tech_level and pattern.rarity == rarity)
            lines.append(f"| Tech {tech_level} {rarity.title()} | {count} | {groups[key]}% |")

    lines.extend(
        [
            "",
            "## Production-Beta Flagship Chain",
            "",
            "| ID | Pattern | Status | Completion |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for row in rows:
        if row.pattern_id not in FLAGSHIP_CHAIN:
            continue
        status = f"{row.implementation}/{row.docs}/{row.tests}"
        lines.append(f"| `{row.pattern_id}` | {row.name} | {status} | {row.percent}% |")

    lines.extend(
        [
            "",
            "## Production-Beta Device Conveyor Chain",
            "",
            "| ID | Pattern | Status | Completion |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for row in rows:
        if row.pattern_id not in DEVICE_TRIGGERED_CONVEYOR_CHAIN:
            continue
        status = f"{row.implementation}/{row.docs}/{row.tests}"
        lines.append(f"| `{row.pattern_id}` | {row.name} | {status} | {row.percent}% |")

    lines.extend(
        [
            "",
            "## Production-Beta Lifecycle Chain",
            "",
            "| ID | Pattern | Status | Completion |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for row in rows:
        if row.pattern_id not in LIFECYCLE_CHAIN:
            continue
        status = f"{row.implementation}/{row.docs}/{row.tests}"
        lines.append(f"| `{row.pattern_id}` | {row.name} | {status} | {row.percent}% |")

    lines.extend(
        [
            "",
            "## Stable Device Conveyor Chain",
            "",
            "| ID | Pattern | Status | Completion |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for row in rows:
        if row.pattern_id not in STABLE_DEVICE_CONVEYOR_CHAIN:
            continue
        status = f"{row.implementation}/{row.docs}/{row.tests}"
        lines.append(f"| `{row.pattern_id}` | {row.name} | {status} | {row.percent}% |")

    lines.extend(
        [
            "",
            "## Full Inventory",
            "",
            "| ID | Pattern | Status | Completion |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for row in rows:
        status = f"{row.implementation}/{row.docs}/{row.tests}"
        lines.append(f"| `{row.pattern_id}` | {row.name} | {status} | {row.percent}% |")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if docs/completion.md is stale")
    args = parser.parse_args()

    output = render()
    if args.check:
        existing = OUT.read_text() if OUT.exists() else ""
        if existing != output:
            print(f"{OUT.relative_to(ROOT)} is stale")
            return 1
        print(f"{OUT.relative_to(ROOT)} is current")
        return 0
    OUT.write_text(output)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
