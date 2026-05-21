from pathlib import Path


def test_manifest_readme_and_units_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "manifest.yaml").exists()
    assert (root / "README.md").exists()
    assert (root / "units/example.service").exists()
    assert (root / "units/example.timer").exists()


def test_pattern_stays_draft() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = (root / "manifest.yaml").read_text(encoding="utf-8")
    assert "id: T2R7.ai-analysis-sidecar" in manifest
    assert "implementation: draft" in manifest
    assert "docs: draft" in manifest
    assert "tests: draft" in manifest
