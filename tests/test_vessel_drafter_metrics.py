import pytest

from programmatic_drafting.analysis.vessel_drafter_metrics import (
    build_material_metrics_report,
)
from programmatic_drafting.models.vessel_drafter import DEFAULT_VESSEL_DRAFTER_LAYOUT
from programmatic_drafting.preview.vessel_drafter_scene import build_vessel_3d_scene


def test_material_metrics_report_includes_refractory_totals() -> None:
    report = build_material_metrics_report(DEFAULT_VESSEL_DRAFTER_LAYOUT)
    metrics_by_label = {item.label: item for item in report.component_metrics}

    assert metrics_by_label["hot_face_refractory"].volume_in3 > 0.0
    assert metrics_by_label["hot_face_refractory"].mass_lb > 0.0
    assert metrics_by_label["hot_face_refractory"].density_lb_per_ft3 > 0.0
    assert metrics_by_label["hot_face_refractory"].thermal_conductivity_w_per_mk > 0.0
    assert metrics_by_label["hot_face_refractory"].thermal_expansion_um_per_m_c > 0.0
    assert report.refractory_total_volume_in3 > 0.0
    assert report.refractory_total_mass_lb > 0.0
    assert report.refractory_total_volume_in3 == pytest.approx(
        sum(
            item.volume_in3
            for item in report.component_metrics
            if item.category == "refractory"
        )
    )


def test_three_d_scene_contains_meshes_for_layers_and_electrodes() -> None:
    scene = build_vessel_3d_scene(DEFAULT_VESSEL_DRAFTER_LAYOUT)
    labels = {mesh.label for mesh in scene.meshes}

    assert "glass_bath" in labels
    assert "steel_shell" in labels
    assert "electrode_1" in labels
    assert all(len(mesh.triangles) > 0 for mesh in scene.meshes)


def test_three_d_scene_respects_visible_label_filter() -> None:
    scene = build_vessel_3d_scene(
        DEFAULT_VESSEL_DRAFTER_LAYOUT,
        visible_labels={"glass_bath", "steel_shell"},
    )

    assert {mesh.label for mesh in scene.meshes} == {"glass_bath", "steel_shell"}
