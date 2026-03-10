import json

from programmatic_drafting.exporters.step_export import export_default_layout_step


def test_export_creates_step_and_manifest(tmp_path) -> None:
    step_path = tmp_path / "electrode_advisor_default_layout.step"
    manifest_path = tmp_path / "electrode_advisor_default_layout.json"

    export_default_layout_step(step_path, manifest_path)

    assert step_path.exists()
    assert step_path.stat().st_size > 0
    assert "ISO-10303-21" in step_path.read_text(encoding="utf-8", errors="ignore")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["project"] == "electrode_advisor_default_layout"
    assert manifest["bath"]["width_m"] == 3.0
    assert len(manifest["placements"]) == 3
