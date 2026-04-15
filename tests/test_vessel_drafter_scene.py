import numpy as np

from programmatic_drafting.preview.vessel_drafter_scene import (
    _cylinder_mesh,
    _revolved_profile_mesh,
    _triangulate_profile_loop,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)
from programmatic_drafting.projects.vessel_drafter_profiles import ProfilePoint


def test_triangulate_profile_loop_returns_expected_triangle_count() -> None:
    triangles = _triangulate_profile_loop(
        (
            ProfilePoint(0.0, 0.0),
            ProfilePoint(2.0, 0.0),
            ProfilePoint(2.0, 1.0),
            ProfilePoint(0.0, 1.0),
        )
    )

    assert len(triangles) == 2


def test_triangulate_profile_loop_returns_empty_for_too_small_loop() -> None:
    assert (
        _triangulate_profile_loop(
            (
                ProfilePoint(0.0, 0.0),
                ProfilePoint(1.0, 1.0),
            )
        )
        == ()
    )


def test_revolved_profile_mesh_uses_stable_counts_and_split_caps() -> None:
    half_profile = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(1.0, 1.0),
        ProfilePoint(0.0, 2.0),
    )

    unsplit_vertices, unsplit_faces = _revolved_profile_mesh(
        half_profile,
        Vessel3DViewOptions(split_enabled=False),
    )
    split_vertices, split_faces = _revolved_profile_mesh(
        half_profile,
        Vessel3DViewOptions(split_enabled=True, split_angle_degrees=30.0),
    )

    assert unsplit_vertices.shape == (26, 3)
    assert unsplit_faces.shape == (48, 3)
    assert split_vertices.shape == (21, 3)
    assert split_faces.shape == (26, 3)


def test_cylinder_mesh_uses_stable_counts_for_vertical_axis() -> None:
    vertices, faces = _cylinder_mesh(
        np.array([0.0, 0.0, 0.0], dtype=np.float64),
        np.array([0.0, 0.0, 5.0], dtype=np.float64),
        1.0,
    )

    assert vertices.shape == (26, 3)
    assert faces.shape == (48, 3)
    assert np.isfinite(vertices).all()
