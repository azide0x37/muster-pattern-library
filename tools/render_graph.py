from __future__ import annotations

import argparse

from patternlib import ROOT, Pattern, validate_all


OUT = ROOT / "docs" / "pattern-graph.md"


def node_id(pattern_id: str) -> str:
    return pattern_id.split(".", 1)[0].replace("-", "_")


def render(patterns: list[Pattern]) -> str:
    lines = [
        "# Muster Pattern Graph",
        "",
        "Generated from manifest `subpatterns` relationships.",
        "",
        "```mermaid",
        "graph TD",
    ]
    for pattern in sorted(patterns, key=lambda item: item.id):
        label = f"{pattern.id}<br/>{pattern.data['name']}"
        lines.append(f'  {node_id(pattern.id)}["{label}"]')
    for pattern in sorted(patterns, key=lambda item: item.id):
        for subpattern in pattern.subpatterns:
            lines.append(f"  {node_id(subpattern)} --> {node_id(pattern.id)}")
    lines.extend(["```", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if docs/pattern-graph.md is stale")
    args = parser.parse_args()

    output = render(validate_all())
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
