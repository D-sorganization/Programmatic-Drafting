import json

from programmatic_drafting.exporters.step_export import (
    export_vessel_drafter_default_step,
)


def test_export_creates_vessel_drafter_step_and_manifest(tmp_path) -> None:
    step_path = tmp_path / "vessel_drafter_default.step"
    manifest_path = tmp_path / "vessel_drafter_default.json"

    export_vessel_drafter_default_step(step_path, manifest_path)

    assert step_path.exists()
    assert step_path.stat().st_size > 0
    assert "ISO-10303-21" in step_path.read_text(encoding="utf-8", errors="ignore")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["project"] == "vessel_drafter_default"
    assert manifest["vessel"]["inner_diameter_in"] == 50.0
    assert manifest["materials"]["steel_shell"]["thickness_in"] == 0.5
    assert manifest["electrodes"]["count"] == 3
