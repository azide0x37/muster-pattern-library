from __future__ import annotations

from patternlib import PatternError, validate_all


def main() -> int:
    try:
        patterns = validate_all()
    except PatternError as exc:
        print(f"validation failed: {exc}")
        return 1
    print(f"validated {len(patterns)} patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
