from pathlib import Path


def test_manifest_exists() -> None:
    assert (Path(__file__).resolve().parents[1] / "manifest.yaml").exists()
