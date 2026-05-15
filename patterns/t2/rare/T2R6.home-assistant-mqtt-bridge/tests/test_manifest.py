from pathlib import Path


def test_manifest_and_readme_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "manifest.yaml").exists()
    assert (root / "README.md").exists()
