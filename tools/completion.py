from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

try:
    from patternlib import Pattern
except ModuleNotFoundError:
    from tools.patternlib import Pattern


STATUS_SCORES = {
    "missing": 0,
    "concept": 10,
    "draft": 33,
    "usable": 70,
    "reviewed": 80,
    "stable": 100,
}

FLAGSHIP_CHAIN = {
    "C1.service-capsule",
    "C2.persistent-tick",
    "C4.lazy-resource-gate",
    "C5.failure-ratchet",
    "TC1.hot-cold-nas-conveyor",
    "TC3.scheduled-herald",
    "TC4.self-healing-reconnector",
    "TC5.local-sidecar-bridge",
    "T3C1.edge-appliance-bundle",
}

PRODUCTION_BETA_STATUS = {
    "implementation": "usable",
    "docs": "reviewed",
    "tests": "reviewed",
}


@dataclass(frozen=True)
class PatternCompletion:
    pattern_id: str
    name: str
    tech_level: int
    rarity: str
    implementation: str
    docs: str
    tests: str
    percent: float


def pattern_percent(pattern: Pattern) -> float:
    status = pattern.data["status"]
    total = (
        STATUS_SCORES[status["implementation"]]
        + STATUS_SCORES[status["docs"]]
        + STATUS_SCORES[status["tests"]]
    )
    return round(total / 3, 1)


def completion_rows(patterns: list[Pattern]) -> list[PatternCompletion]:
    rows: list[PatternCompletion] = []
    for pattern in sorted(patterns, key=lambda item: (item.tech_level, item.rarity, item.id)):
        status = pattern.data["status"]
        rows.append(
            PatternCompletion(
                pattern_id=pattern.id,
                name=pattern.data["name"],
                tech_level=pattern.tech_level,
                rarity=pattern.rarity,
                implementation=status["implementation"],
                docs=status["docs"],
                tests=status["tests"],
                percent=pattern_percent(pattern),
            )
        )
    return rows


def overall_percent(patterns: list[Pattern]) -> float:
    if not patterns:
        return 0.0
    return round(sum(pattern_percent(pattern) for pattern in patterns) / len(patterns), 1)


def grouped_percentages(patterns: list[Pattern]) -> dict[tuple[int, str], float]:
    groups: dict[tuple[int, str], list[float]] = defaultdict(list)
    for pattern in patterns:
        groups[(pattern.tech_level, pattern.rarity)].append(pattern_percent(pattern))
    return {
        key: round(sum(values) / len(values), 1)
        for key, values in sorted(groups.items())
        if values
    }


def is_production_beta(pattern: Pattern) -> bool:
    return pattern.data["status"] == PRODUCTION_BETA_STATUS
