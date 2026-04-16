from __future__ import annotations

from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    VesselDrafterLayout,
    VesselLidPort,
    VesselSidePort,
    _build_drafting_assumptions_manifest,
    _build_glass_bath_manifest,
    _build_lid_port_manifest,
    _build_ports_manifest,
    _build_shell_materials_manifest,
    _build_side_port_manifest,
    _build_vessel_manifest,
    build_vessel_drafter_manifest,
)


def test_build_vessel_manifest_reports_layout_geometry() -> None:
    manifest = _build_vessel_manifest(DEFAULT_VESSEL_DRAFTER_LAYOUT)

    assert manifest["inner_diameter_in"] == 50.0
    assert manifest["outer_diameter_in"] == 74.0
    assert manifest["full_height_in"] == DEFAULT_VESSEL_DRAFTER_LAYOUT.full_height_in


def test_build_shell_materials_manifest_includes_shell_layers() -> None:
    materials = _build_shell_materials_manifest(
        DEFAULT_VESSEL_DRAFTER_LAYOUT.layers[1:]
    )

    assert set(materials) == {
        "hot_face_refractory",
        "ifb",
        "duraboard",
        "steel_shell",
    }
    assert materials["steel_shell"]["thickness_in"] == 0.5
    assert materials["steel_shell"]["display_name"] == "Steel Shell"


def test_build_glass_bath_manifest_uses_glass_layer_properties() -> None:
    layer = DEFAULT_VESSEL_DRAFTER_LAYOUT.layers[0]

    manifest = _build_glass_bath_manifest(
        layer,
        DEFAULT_VESSEL_DRAFTER_LAYOUT.glass_depth_in,
    )

    assert manifest["display_name"] == "Glass Bath"
    assert manifest["height_in"] == 14.0
    assert manifest["color_hex"] == layer.color_hex


def test_build_vessel_drafter_manifest_includes_all_sections() -> None:
    manifest = build_vessel_drafter_manifest(DEFAULT_VESSEL_DRAFTER_LAYOUT)

    assert manifest["project"] == "vessel_drafter_default"
    assert manifest["units"] == {"source": "inches", "cad": "millimeters"}
    assert manifest["vessel"]["outer_head_depth_in"] == 24.5
    assert manifest["materials"]["steel_shell"]["thickness_in"] == 0.5
    assert manifest["glass_bath"]["display_name"] == "Glass Bath"
    assert manifest["electrodes"]["modeled_length_in"] == 50.0
    assert manifest["ports"] == {"side": [], "lid": []}
    assert manifest["drafting_assumptions"]["axis_convention"] == "Z up"


def test_layout_to_manifest_delegates_to_manifest_helper() -> None:
    manifest = DEFAULT_VESSEL_DRAFTER_LAYOUT.to_manifest()

    assert manifest == build_vessel_drafter_manifest(DEFAULT_VESSEL_DRAFTER_LAYOUT)


def test_build_port_manifest_helpers_track_layout_geometry() -> None:
    layout = VesselDrafterLayout(
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
    )

    side_port = _build_side_port_manifest(layout, layout.side_ports[0])
    lid_port = _build_lid_port_manifest(layout.lid_ports[0])
    ports = _build_ports_manifest(layout)

    assert side_port["centerline_height_in"] == 18.0
    assert lid_port["radial_distance_from_center_in"] == 6.0
    assert ports["side"][0] == side_port
    assert ports["lid"][0] == lid_port


def test_build_drafting_assumptions_manifest_is_stable() -> None:
    manifest = _build_drafting_assumptions_manifest()

    assert manifest == {
        "axis_convention": "Z up",
        "plenum_only_internal_void": True,
        "dished_heads": (
            "Offset elliptical head profiles with constant-thickness shell layers"
        ),
    }
