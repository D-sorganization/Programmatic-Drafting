import json

from programmatic_drafting.exporters.step_export import (
    export_vessel_drafter_default_step,
    export_vessel_drafter_step,
)
from programmatic_drafting.models.vessel_drafter import (
    VesselDrafterLayout,
    VesselLidPort,
    VesselSidePort,
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


def test_export_manifest_includes_port_configuration(tmp_path) -> None:
    step_path = tmp_path / "ported_vessel.step"
    manifest_path = tmp_path / "ported_vessel.json"

    export_vessel_drafter_step(
        output_path=step_path,
        manifest_path=manifest_path,
        layout=VesselDrafterLayout(
            side_ports=(
                VesselSidePort(
                    clock_angle_degrees=45.0,
                    diameter_in=3.0,
                    height_above_glass_surface_in=4.0,
                ),
            ),
            lid_ports=(
                VesselLidPort(
                    clock_angle_degrees=180.0,
                    diameter_in=4.0,
                    radial_distance_from_center_in=6.0,
                ),
            ),
        ),
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["ports"]["side"][0]["diameter_in"] == 3.0
    assert manifest["ports"]["lid"][0]["radial_distance_from_center_in"] == 6.0
