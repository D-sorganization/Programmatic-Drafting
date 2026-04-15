import numpy as np

from programmatic_drafting.preview._vessel_drafter_scene_section import (
    _triangulate_profile_loop,
    maybe_apply_section_cut,
    section_cap_mesh,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)
from programmatic_drafting.projects.vessel_drafter_profiles import ProfilePoint


def test_triangulate_profile_loop_uses_ear_clipping_for_concave_profile() -> None:
    profile = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(2.0, 0.0),
        ProfilePoint(2.0, 1.0),
        ProfilePoint(1.0, 0.5),
        ProfilePoint(0.0, 1.0),
    )

    triangles = _triangulate_profile_loop(profile)

    assert triangles == ((1, 2, 3), (0, 1, 3), (0, 3, 4))


def test_section_cap_mesh_mirrors_vertices_and_reverses_back_faces() -> None:
    profile = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(1.0, 0.0),
        ProfilePoint(0.0, 1.0),
    )
    view_options = Vessel3DViewOptions(
        split_enabled=True,
        split_angle_degrees=30.0,
    )

    vertices, faces = section_cap_mesh(profile, view_options)

    assert vertices.shape == (6, 3)
    assert faces.shape == (2, 3)
    assert np.allclose(vertices[:3, 2], [0.0, 0.0, 1.0])
    assert np.allclose(vertices[3:, 2], [0.0, 0.0, 1.0])
    assert np.array_equal(faces[0], [0, 1, 2])
    assert np.array_equal(faces[1], [5, 4, 3])


def test_maybe_apply_section_cut_discards_faces_behind_split_plane() -> None:
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [1.0, -1.0, 0.0],
            [0.0, -2.0, 0.0],
        ],
        dtype=np.float64,
    )
    faces = np.array(
        [
            [0, 1, 2],
            [3, 4, 5],
        ],
        dtype=np.int32,
    )
    view_options = Vessel3DViewOptions(
        split_enabled=True,
        split_angle_degrees=0.0,
    )

    filtered_vertices, filtered_faces = maybe_apply_section_cut(
        (vertices, faces),
        view_options,
    )

    assert filtered_vertices is vertices
    assert filtered_faces.shape == (1, 3)
    assert np.array_equal(filtered_faces[0], [0, 1, 2])
