from programmatic_drafting.models.vessel_drafter import (
    VesselDrafterLayout,
    VesselLidPort,
    VesselSidePort,
)
from programmatic_drafting.preview import vessel_drafter_scene as scene_module
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)


def test_scene_mesh_selection_uses_fast_builder_for_plain_layout(
    monkeypatch,
) -> None:
    layout = VesselDrafterLayout()
    fast_meshes = ("fast",)
    exact_meshes = ("exact",)

    monkeypatch.setattr(
        scene_module,
        "build_fast_meshes",
        lambda *args: fast_meshes,
    )
    monkeypatch.setattr(
        scene_module,
        "build_exact_meshes",
        lambda *args: exact_meshes,
    )

    result = scene_module._build_vessel_3d_scene_meshes(
        layout,
        None,
        Vessel3DViewOptions(),
    )

    assert result == fast_meshes


def test_scene_mesh_selection_uses_exact_builder_when_ports_exist(
    monkeypatch,
) -> None:
    layout = VesselDrafterLayout(
        side_ports=(
            VesselSidePort(
                clock_angle_degrees=30.0,
                diameter_in=3.0,
                height_above_glass_surface_in=6.0,
            ),
        ),
        lid_ports=(
            VesselLidPort(
                clock_angle_degrees=225.0,
                diameter_in=4.0,
                radial_distance_from_center_in=8.0,
            ),
        ),
    )
    fast_meshes = ("fast",)
    exact_meshes = ("exact",)

    monkeypatch.setattr(
        scene_module,
        "build_fast_meshes",
        lambda *args: fast_meshes,
    )
    monkeypatch.setattr(
        scene_module,
        "build_exact_meshes",
        lambda *args: exact_meshes,
    )

    result = scene_module._build_vessel_3d_scene_meshes(
        layout,
        {"side_ports"},
        Vessel3DViewOptions(),
    )

    assert result == exact_meshes
