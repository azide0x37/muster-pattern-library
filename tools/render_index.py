from __future__ import annotations

import argparse
from pathlib import Path

from patternlib import ROOT, Pattern, validate_all


OUT = ROOT / "docs" / "index.md"


def render(patterns: list[Pattern]) -> str:
    groups: dict[tuple[int, str], list[Pattern]] = {}
    for pattern in patterns:
        groups.setdefault((pattern.tech_level, pattern.rarity), []).append(pattern)

    lines = [
        "# Muster Pattern Index",
        "",
        "Generated from `patterns/**/manifest.yaml`.",
        "",
    ]
    for tech_level in [1, 2, 3]:
        lines.append(f"## Tech {tech_level}")
        lines.append("")
        for rarity in ["common", "rare", "mythic"]:
            members = sorted(groups.get((tech_level, rarity), []), key=lambda item: item.id)
            if not members:
                continue
            lines.append(f"### {rarity.title()}")
            lines.append("")
            lines.append("| ID | Pattern | MRL | Subpatterns | Status |")
            lines.append("| --- | --- | ---: | --- | --- |")
            for pattern in members:
                data = pattern.data
                subpatterns = ", ".join(data["subpatterns"]) if data["subpatterns"] else "-"
                status = "/".join(
                    [
                        data["status"]["implementation"],
                        data["status"]["docs"],
                        data["status"]["tests"],
                    ]
                )
                rel = pattern.path.parent.relative_to(ROOT)
                lines.append(
                    f"| [`{pattern.id}`](../{rel}/) | {data['name']} | {data['mrl']} | {subpatterns} | {status} |"
                )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if docs/index.md is stale")
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
