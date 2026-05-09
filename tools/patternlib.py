from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATTERNS_DIR = ROOT / "patterns"

VALID_RARITIES = {"common", "rare", "mythic"}
VALID_STATUS = {
    "implementation": {"concept", "draft", "usable", "stable"},
    "docs": {"draft", "reviewed", "stable"},
    "tests": {"missing", "draft", "reviewed", "stable"},
}
VALID_LIFECYCLE_INSTALL_MODES = {"dry_run", "staged_root", "apply"}
VALID_LIFECYCLE_DOCTOR_MODES = {"local", "mock", "staged_root"}
VALID_LIFECYCLE_ROLLBACK = {"documented", "artifact_generation", "doctor_gated"}
VALID_LIFECYCLE_UNINSTALL = {"documented", "artifacts_only"}
VALID_LIFECYCLE_UPDATE = {"none", "manifest_sha256", "signed_manifest"}

REQUIRED_README_SECTIONS = [
    "## Intent",
    "## When to use this",
    "## When not to use this",
    "## System shape",
    "## Subpatterns",
    "## Files",
    "## Installation",
    "## Verification",
    "## Failure modes",
    "## Rollback",
    "## Security notes",
    "## Future work",
]

ID_RE = re.compile(r"^(C|R|M|T2C|T2R|T2M|T3C|T3R|T3M)([0-9]+)\.[a-z0-9]+(?:-[a-z0-9]+)*$")


class PatternError(Exception):
    """Raised when a pattern contract is invalid."""


@dataclass(frozen=True)
class Pattern:
    path: Path
    data: dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.data["id"])

    @property
    def tech_level(self) -> int:
        return int(self.data["tech_level"])

    @property
    def rarity(self) -> str:
        return str(self.data["rarity"])

    @property
    def subpatterns(self) -> list[str]:
        return list(self.data.get("subpatterns", []))


def _active_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw.strip()))
    return lines


def _parse_scalar(value: str) -> Any:
    if value == "[]":
        return []
    if value in {"true", "false"}:
        return value == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    return value


def load_simple_yaml(path: Path) -> dict[str, Any]:
    lines = _active_lines(path.read_text())

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(lines):
            return {}, index
        current_indent, stripped = lines[index]
        if current_indent != indent:
            raise PatternError(f"{path}: expected indent {indent}, got {current_indent}")
        if stripped.startswith("- "):
            return parse_list(index, indent)
        return parse_mapping(index, indent)

    def parse_mapping(index: int, indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while index < len(lines):
            current_indent, stripped = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise PatternError(f"{path}: unexpected indent before {stripped!r}")
            if stripped.startswith("- "):
                break
            if ":" not in stripped:
                raise PatternError(f"{path}: expected key/value line, got {stripped!r}")
            key, raw_value = stripped.split(":", 1)
            value = raw_value.strip()
            if value == ">":
                index += 1
                folded: list[str] = []
                while index < len(lines) and lines[index][0] > current_indent:
                    folded.append(lines[index][1])
                    index += 1
                result[key] = " ".join(folded).strip()
            elif value:
                result[key] = _parse_scalar(value)
                index += 1
            else:
                index += 1
                if index >= len(lines) or lines[index][0] <= current_indent:
                    result[key] = None
                else:
                    result[key], index = parse_block(index, lines[index][0])
        return result, index

    def parse_list(index: int, indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while index < len(lines):
            current_indent, stripped = lines[index]
            if current_indent < indent:
                break
            if current_indent != indent or not stripped.startswith("- "):
                break
            value = stripped[2:].strip()
            if value:
                result.append(_parse_scalar(value))
                index += 1
            else:
                index += 1
                if index >= len(lines):
                    result.append(None)
                else:
                    child, index = parse_block(index, lines[index][0])
                    result.append(child)
        return result, index

    parsed, next_index = parse_block(0, 0)
    if next_index != len(lines):
        raise PatternError(f"{path}: trailing unparsable content")
    if not isinstance(parsed, dict):
        raise PatternError(f"{path}: manifest root must be a mapping")
    return parsed


def discover_manifest_paths(root: Path = PATTERNS_DIR) -> list[Path]:
    return sorted(root.glob("**/manifest.yaml"))


def load_patterns(root: Path = PATTERNS_DIR) -> list[Pattern]:
    return [Pattern(path=path, data=load_simple_yaml(path)) for path in discover_manifest_paths(root)]


def pattern_index(patterns: list[Pattern]) -> dict[str, Pattern]:
    index: dict[str, Pattern] = {}
    for pattern in patterns:
        if pattern.id in index:
            raise PatternError(f"duplicate pattern id: {pattern.id}")
        index[pattern.id] = pattern
    return index


def validate_id_shape(data: dict[str, Any], path: Path) -> None:
    pattern_id = data.get("id")
    if not isinstance(pattern_id, str) or not ID_RE.match(pattern_id):
        raise PatternError(f"{path}: invalid id {pattern_id!r}")

    prefix = ID_RE.match(pattern_id).group(1)  # type: ignore[union-attr]
    tech_level = data.get("tech_level")
    rarity = data.get("rarity")
    expected = {
        (1, "common"): {"C"},
        (1, "rare"): {"R"},
        (1, "mythic"): {"M"},
        (2, "common"): {"T2C"},
        (2, "rare"): {"T2R"},
        (2, "mythic"): {"T2M"},
        (3, "common"): {"T3C"},
        (3, "rare"): {"T3R"},
        (3, "mythic"): {"T3M"},
    }.get((tech_level, rarity))
    if expected is None or prefix not in expected:
        raise PatternError(f"{path}: id prefix {prefix!r} does not match tech/rarity")


def validate_manifest_shape(pattern: Pattern) -> None:
    data = pattern.data
    path = pattern.path
    required = {
        "id",
        "name",
        "tech_level",
        "rarity",
        "mrl",
        "summary",
        "provides",
        "requires",
        "subpatterns",
        "composes_with",
        "artifacts",
        "status",
    }
    missing = sorted(required - set(data))
    if missing:
        raise PatternError(f"{path}: missing required fields: {', '.join(missing)}")

    validate_id_shape(data, path)

    if data["tech_level"] not in {1, 2, 3}:
        raise PatternError(f"{path}: tech_level must be 1, 2, or 3")
    if data["rarity"] not in VALID_RARITIES:
        raise PatternError(f"{path}: invalid rarity {data['rarity']!r}")
    if not isinstance(data["mrl"], int) or not (1 <= data["mrl"] <= 9):
        raise PatternError(f"{path}: mrl must be an integer from 1 to 9")
    for key in ["provides", "requires", "subpatterns", "composes_with"]:
        if not isinstance(data[key], list) or not all(isinstance(item, str) for item in data[key]):
            raise PatternError(f"{path}: {key} must be a list of strings")
    if not data["provides"]:
        raise PatternError(f"{path}: provides must not be empty")
    if not isinstance(data["artifacts"], dict):
        raise PatternError(f"{path}: artifacts must be a mapping")
    for artifact_key, artifact_paths in data["artifacts"].items():
        if not isinstance(artifact_key, str):
            raise PatternError(f"{path}: artifact keys must be strings")
        if not isinstance(artifact_paths, list) or not all(isinstance(item, str) for item in artifact_paths):
            raise PatternError(f"{path}: artifacts.{artifact_key} must be a list of strings")
    if not isinstance(data["status"], dict):
        raise PatternError(f"{path}: status must be a mapping")
    for key, allowed in VALID_STATUS.items():
        if data["status"].get(key) not in allowed:
            raise PatternError(f"{path}: status.{key} has invalid value {data['status'].get(key)!r}")

    lifecycle = data.get("lifecycle")
    if lifecycle is not None:
        validate_lifecycle_shape(lifecycle, path)


def _validate_string_list(value: Any, allowed: set[str], label: str, path: Path) -> None:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise PatternError(f"{path}: lifecycle.{label} must be a non-empty list of strings")
    invalid = sorted(set(value) - allowed)
    if invalid:
        raise PatternError(f"{path}: lifecycle.{label} has invalid values: {', '.join(invalid)}")


def validate_lifecycle_shape(lifecycle: Any, path: Path) -> None:
    if not isinstance(lifecycle, dict):
        raise PatternError(f"{path}: lifecycle must be a mapping")
    required = {"managed", "install_modes", "doctor_modes", "rollback", "uninstall", "update"}
    missing = sorted(required - set(lifecycle))
    if missing:
        raise PatternError(f"{path}: lifecycle missing required fields: {', '.join(missing)}")
    if not isinstance(lifecycle["managed"], bool):
        raise PatternError(f"{path}: lifecycle.managed must be true or false")
    _validate_string_list(lifecycle["install_modes"], VALID_LIFECYCLE_INSTALL_MODES, "install_modes", path)
    _validate_string_list(lifecycle["doctor_modes"], VALID_LIFECYCLE_DOCTOR_MODES, "doctor_modes", path)
    for key, allowed in {
        "rollback": VALID_LIFECYCLE_ROLLBACK,
        "uninstall": VALID_LIFECYCLE_UNINSTALL,
        "update": VALID_LIFECYCLE_UPDATE,
    }.items():
        if lifecycle[key] not in allowed:
            raise PatternError(f"{path}: lifecycle.{key} has invalid value {lifecycle[key]!r}")


def validate_folder_contract(pattern: Pattern) -> None:
    folder = pattern.path.parent
    if folder.name != pattern.id:
        raise PatternError(f"{pattern.path}: folder name must be exactly {pattern.id}")

    expected_parts = ["patterns", f"t{pattern.tech_level}", pattern.rarity]
    if list(folder.relative_to(ROOT).parts[:3]) != expected_parts:
        raise PatternError(f"{pattern.path}: folder path must start with {'/'.join(expected_parts)}")

    readme = folder / "README.md"
    if not readme.exists():
        raise PatternError(f"{pattern.path}: README.md is missing")
    text = readme.read_text()
    for section in REQUIRED_README_SECTIONS:
        if section not in text:
            raise PatternError(f"{readme}: missing required section {section}")

    for dirname in ["units", "scripts", "tests", "examples"]:
        if not (folder / dirname).exists():
            raise PatternError(f"{pattern.path}: missing {dirname}/ directory")

    for artifact_paths in pattern.data["artifacts"].values():
        for relpath in artifact_paths:
            if not (folder / relpath).exists():
                raise PatternError(f"{pattern.path}: artifact does not exist: {relpath}")


def composition_allowed(parent: Pattern, child: Pattern) -> bool:
    parent_key = (parent.tech_level, parent.rarity)
    child_key = (child.tech_level, child.rarity)
    allowed: dict[tuple[int, str], set[tuple[int, str]]] = {
        (1, "common"): set(),
        (1, "rare"): set(),
        (1, "mythic"): set(),
        (2, "common"): {(1, "common")},
        (2, "rare"): {(1, "common"), (1, "rare"), (2, "common")},
        (2, "mythic"): {
            (1, "common"),
            (1, "rare"),
            (1, "mythic"),
            (2, "common"),
            (2, "rare"),
        },
        (3, "common"): {(1, "common"), (2, "common")},
        (3, "rare"): {
            (1, "common"),
            (1, "rare"),
            (2, "common"),
            (2, "rare"),
            (3, "common"),
        },
        (3, "mythic"): {
            (1, "common"),
            (1, "rare"),
            (1, "mythic"),
            (2, "common"),
            (2, "rare"),
            (2, "mythic"),
            (3, "common"),
            (3, "rare"),
        },
    }
    return child_key in allowed[parent_key]


def validate_composition(patterns: list[Pattern]) -> None:
    index = pattern_index(patterns)
    for pattern in patterns:
        if pattern.tech_level == 1 and pattern.subpatterns:
            raise PatternError(f"{pattern.path}: Tech I patterns must not declare subpatterns")
        for subpattern_id in pattern.subpatterns:
            child = index.get(subpattern_id)
            if child is None:
                raise PatternError(f"{pattern.path}: unknown subpattern {subpattern_id}")
            if child.id == pattern.id:
                raise PatternError(f"{pattern.path}: pattern cannot depend on itself")
            if not composition_allowed(pattern, child):
                raise PatternError(
                    f"{pattern.path}: {pattern.id} may not compose {child.id} under current rules"
                )


def validate_all(root: Path = PATTERNS_DIR) -> list[Pattern]:
    patterns = load_patterns(root)
    for pattern in patterns:
        validate_manifest_shape(pattern)
        validate_folder_contract(pattern)
    validate_composition(patterns)
    return patterns
