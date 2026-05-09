from __future__ import annotations

from patternlib import PatternError, load_patterns, validate_composition


def main() -> int:
    try:
        patterns = load_patterns()
        validate_composition(patterns)
    except PatternError as exc:
        print(f"composition failed: {exc}")
        return 1
    print(f"composition ok for {len(patterns)} patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
