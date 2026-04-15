"""Dedicated tests for mesh-construction primitives in the vessel 3D scene.

Issue #21 calls out the mesh builders as untested. Those primitives live in the
focused sub-modules under ``programmatic_drafting.preview.*_scene_*`` (PR #55
split the original ``vessel_drafter_scene`` into sub-modules — this test file
exercises them directly rather than through the public facade).

Covered primitives:

* ``cylinder_mesh`` — cylinder vertex / face construction with end caps.
* ``revolved_profile_mesh`` — surface of revolution for a (r, z) profile.
* ``section_cap_mesh`` — planar triangulation for the cut plane in split view.
* ``preview_angles`` — angle sample generator for full vs split revolution.
* ``maybe_apply_section_cut`` — half-space face filter for split view.
* ``scene_bounds`` / ``make_mesh`` — bounding-box aggregation and mesh factory.
"""

from __future__ import annotations

from math import pi

import numpy as np
import pytest

from programmatic_drafting.preview._vessel_drafter_scene_common import (
    DEFAULT_ANGULAR_SEGMENTS,
    DEFAULT_ELECTRODE_SEGMENTS,
    VesselSceneMesh,
    make_mesh,
    scene_bounds,
)
from programmatic_drafting.preview._vessel_drafter_scene_cylinder import (
    cylinder_mesh,
)
from programmatic_drafting.preview._vessel_drafter_scene_revolution import (
    revolved_profile_mesh,
)
from programmatic_drafting.preview._vessel_drafter_scene_section import (
    maybe_apply_section_cut,
    preview_angles,
    section_cap_mesh,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)
from programmatic_drafting.projects.vessel_drafter_profiles import ProfilePoint

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _triangle_mesh_surface_area(vertices: np.ndarray, faces: np.ndarray) -> float:
    """Sum of absolute triangle areas for a triangle-face mesh."""
    triangles = vertices[faces]
    edge_a = triangles[:, 1] - triangles[:, 0]
    edge_b = triangles[:, 2] - triangles[:, 0]
    cross = np.cross(edge_a, edge_b)
    return float(0.5 * np.linalg.norm(cross, axis=1).sum())


# ---------------------------------------------------------------------------
# cylinder_mesh
# ---------------------------------------------------------------------------


def test_cylinder_mesh_axis_aligned_has_expected_vertex_and_face_counts() -> None:
    start = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    end = np.array([0.0, 0.0, 2.0], dtype=np.float64)

    vertices, faces = cylinder_mesh(start, end, radius_in=1.0)

    # Two rings of N segments + two cap-center points.
    assert vertices.shape == (2 * DEFAULT_ELECTRODE_SEGMENTS + 2, 3)
    # Two triangles per side quad + one triangle per cap segment on each cap.
    assert faces.shape == (4 * DEFAULT_ELECTRODE_SEGMENTS, 3)
    # All face indices reference the returned vertex array.
    assert faces.min() >= 0
    assert faces.max() == 2 * DEFAULT_ELECTRODE_SEGMENTS + 1


def test_cylinder_mesh_cap_centers_are_axis_endpoints() -> None:
    start = np.array([1.0, 2.0, -3.0], dtype=np.float64)
    end = np.array([1.0, 2.0, 4.0], dtype=np.float64)

    vertices, _ = cylinder_mesh(start, end, radius_in=0.5)

    # By construction the last two vertices are the two cap-center points.
    np.testing.assert_allclose(vertices[-2], start)
    np.testing.assert_allclose(vertices[-1], end)


def test_cylinder_mesh_ring_vertices_lie_on_cylinder_surface() -> None:
    start = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    end = np.array([0.0, 0.0, 5.0], dtype=np.float64)
    radius = 1.5

    vertices, _ = cylinder_mesh(start, end, radius_in=radius)

    ring_points = vertices[: 2 * DEFAULT_ELECTRODE_SEGMENTS]
    radii = np.sqrt(ring_points[:, 0] ** 2 + ring_points[:, 1] ** 2)
    # Every ring vertex sits exactly on the lateral surface.
    np.testing.assert_allclose(radii, radius, atol=1e-12)
    # Lower ring z == start.z, upper ring z == end.z.
    np.testing.assert_allclose(
        ring_points[:DEFAULT_ELECTRODE_SEGMENTS, 2], 0.0, atol=1e-12
    )
    np.testing.assert_allclose(
        ring_points[DEFAULT_ELECTRODE_SEGMENTS:, 2], 5.0, atol=1e-12
    )


def test_cylinder_mesh_surface_area_matches_inscribed_prism() -> None:
    # The mesh is a 12-gon prism inscribed in the true cylinder. Closed-form
    # lateral area = N * chord * h where chord = 2 * r * sin(pi/N), and each
    # cap is a regular N-gon with area = 0.5 * N * r^2 * sin(2*pi/N).
    start = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    end = np.array([0.0, 0.0, 2.0], dtype=np.float64)
    radius = 1.0

    vertices, faces = cylinder_mesh(start, end, radius_in=radius)

    lateral_area = (
        DEFAULT_ELECTRODE_SEGMENTS
        * 2.0
        * radius
        * np.sin(pi / DEFAULT_ELECTRODE_SEGMENTS)
        * 2.0
    )
    cap_area = (
        0.5
        * DEFAULT_ELECTRODE_SEGMENTS
        * radius**2
        * np.sin(2.0 * pi / DEFAULT_ELECTRODE_SEGMENTS)
    )
    expected = lateral_area + 2.0 * cap_area

    observed = _triangle_mesh_surface_area(vertices, faces)
    assert observed == pytest.approx(expected, rel=1e-12)
    # Sanity: slightly below the true cylinder surface area 2*pi*r*h + 2*pi*r^2.
    true_cylinder_surface = 2.0 * pi * radius * 2.0 + 2.0 * pi * radius**2
    assert observed < true_cylinder_surface
    assert observed > 0.9 * true_cylinder_surface


def test_cylinder_mesh_radial_frame_is_orthogonal_for_off_axis_cylinder() -> None:
    # Non-axis-aligned cylinder: the constructed ring must still have every
    # vertex at the requested radius (i.e. frame vectors are orthonormal).
    start = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    end = np.array([3.0, 4.0, 0.0], dtype=np.float64)
    radius = 2.0

    vertices, _ = cylinder_mesh(start, end, radius_in=radius)

    axis = (end - start) / np.linalg.norm(end - start)
    ring_points = vertices[: 2 * DEFAULT_ELECTRODE_SEGMENTS]
    # Decompose each ring point onto the axis; the residual perpendicular
    # component must equal the radius exactly.
    offsets = ring_points - np.where(
        np.arange(len(ring_points))[:, None] < DEFAULT_ELECTRODE_SEGMENTS,
        start,
        end,
    )
    axial_components = offsets @ axis
    perpendicular = offsets - axial_components[:, None] * axis
    perpendicular_radii = np.linalg.norm(perpendicular, axis=1)
    np.testing.assert_allclose(perpendicular_radii, radius, atol=1e-12)
    # And the axial component is zero for every ring vertex (rings lie in the
    # two end planes).
    np.testing.assert_allclose(axial_components, 0.0, atol=1e-12)


# ---------------------------------------------------------------------------
# revolved_profile_mesh
# ---------------------------------------------------------------------------


def _rectangle_profile() -> tuple[ProfilePoint, ...]:
    """Rectangular profile that revolves into a disc of radius 1, height 2."""
    return (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(1.0, 0.0),
        ProfilePoint(1.0, 2.0),
        ProfilePoint(0.0, 2.0),
    )


def test_revolved_profile_mesh_full_rotation_counts_match_schema() -> None:
    profile = _rectangle_profile()

    vertices, faces = revolved_profile_mesh(profile, Vessel3DViewOptions())

    # Two axis points contribute a single vertex each, two off-axis points
    # contribute a ring of DEFAULT_ANGULAR_SEGMENTS vertices each.
    expected_vertex_count = 2 + 2 * DEFAULT_ANGULAR_SEGMENTS
    assert vertices.shape == (expected_vertex_count, 3)

    # Four profile segments: axis->ring (fan), ring->ring (quad belt),
    # ring->axis (fan), axis->axis (empty). With full wrap each fan produces
    # N triangles and each belt produces 2*N. Axis-axis yields zero faces.
    expected_face_count = (
        DEFAULT_ANGULAR_SEGMENTS  # bottom fan (axis -> lower ring)
        + 2 * DEFAULT_ANGULAR_SEGMENTS  # side belt (lower ring -> upper ring)
        + DEFAULT_ANGULAR_SEGMENTS  # top fan (upper ring -> axis)
        + 0  # axis -> axis (no faces)
    )
    assert faces.shape == (expected_face_count, 3)
    assert faces.min() >= 0
    assert faces.max() == expected_vertex_count - 1


def test_revolved_profile_mesh_rectangle_bounds_match_profile_extent() -> None:
    profile = _rectangle_profile()

    vertices, _ = revolved_profile_mesh(profile, Vessel3DViewOptions())

    assert vertices[:, 0].min() == pytest.approx(-1.0, abs=1e-12)
    assert vertices[:, 0].max() == pytest.approx(1.0, abs=1e-12)
    assert vertices[:, 1].min() == pytest.approx(-1.0, abs=1e-12)
    assert vertices[:, 1].max() == pytest.approx(1.0, abs=1e-12)
    assert vertices[:, 2].min() == pytest.approx(0.0, abs=1e-12)
    assert vertices[:, 2].max() == pytest.approx(2.0, abs=1e-12)


def test_revolved_profile_mesh_surface_area_matches_inscribed_prism() -> None:
    profile = _rectangle_profile()

    vertices, faces = revolved_profile_mesh(profile, Vessel3DViewOptions())

    # The revolved rectangle is a 24-gonal prism inscribed in the unit
    # cylinder of height 2. Expected surface = 2 * N-gon cap + N-gon belt.
    cap_area = (
        0.5
        * DEFAULT_ANGULAR_SEGMENTS
        * 1.0**2
        * np.sin(2.0 * pi / DEFAULT_ANGULAR_SEGMENTS)
    )
    lateral_area = (
        DEFAULT_ANGULAR_SEGMENTS
        * 2.0
        * 1.0
        * np.sin(pi / DEFAULT_ANGULAR_SEGMENTS)
        * 2.0
    )
    expected_area = 2.0 * cap_area + lateral_area

    observed_area = _triangle_mesh_surface_area(vertices, faces)
    assert observed_area == pytest.approx(expected_area, rel=1e-12)


def test_revolved_profile_mesh_split_view_uses_half_revolution_counts() -> None:
    profile = _rectangle_profile()
    split_options = Vessel3DViewOptions(split_enabled=True, split_angle_degrees=0.0)

    vertices, faces = revolved_profile_mesh(profile, split_options)

    # Split view samples (N/2 + 1) angles across a half turn plus the section
    # cap. The rectangle profile has 4 points; 2 are off-axis so they each
    # contribute (N/2 + 1) ring vertices. The two axis points contribute one
    # vertex each. Section cap adds 2 * len(profile) = 8 vertices.
    half_ring = (DEFAULT_ANGULAR_SEGMENTS // 2) + 1
    expected_body_vertices = 2 + 2 * half_ring
    expected_total_vertices = expected_body_vertices + 2 * len(profile)
    assert vertices.shape == (expected_total_vertices, 3)

    # Faces still present and strictly fewer than the full-rotation case.
    full_vertices, full_faces = revolved_profile_mesh(profile, Vessel3DViewOptions())
    assert faces.shape[0] < full_faces.shape[0]
    assert full_vertices.shape[0] > 0  # sanity cross-check
    assert faces.size > 0


def test_revolved_profile_mesh_all_axis_points_is_degenerate() -> None:
    # Every profile point lies exactly on the symmetry axis, so no ring is
    # ever emitted and no belt faces can be generated. The current builder
    # relies on ``np.vstack`` of the face parts, so this degenerate case
    # raises ``ValueError`` — pin that contract so a future change to
    # silently return an empty face array is caught here.
    axis_only = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(0.0, 1.0),
        ProfilePoint(0.0, 2.0),
    )

    with pytest.raises(ValueError, match="at least one array"):
        revolved_profile_mesh(axis_only, Vessel3DViewOptions())


def test_revolved_profile_mesh_single_offaxis_point_above_axis_creates_cone_fan() -> (
    None
):
    # Minimal non-degenerate profile: axis apex -> off-axis ring -> axis apex.
    # Forms a bicone. Validates belt-free construction (only fan faces).
    bicone_profile = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(1.0, 1.0),
        ProfilePoint(0.0, 2.0),
    )

    vertices, faces = revolved_profile_mesh(bicone_profile, Vessel3DViewOptions())

    # Two apex vertices + one ring of N vertices.
    assert vertices.shape == (2 + DEFAULT_ANGULAR_SEGMENTS, 3)
    # Two fans of N triangles each.
    assert faces.shape == (2 * DEFAULT_ANGULAR_SEGMENTS, 3)
    # Bicone apex-to-ring slant distance is sqrt(2), so lateral = 2 * pyramidal.
    # Each pyramid is a regular N-gon cone; its lateral area is
    # 0.5 * N * base_chord * slant_height_face, where slant_height_face is the
    # distance from apex to a chord midpoint. This is harder to pin in closed
    # form, so just check monotonic positivity + bbox bounds instead.
    assert _triangle_mesh_surface_area(vertices, faces) > 0.0
    assert vertices[:, 2].min() == pytest.approx(0.0, abs=1e-12)
    assert vertices[:, 2].max() == pytest.approx(2.0, abs=1e-12)


# ---------------------------------------------------------------------------
# section_cap_mesh
# ---------------------------------------------------------------------------


def test_section_cap_mesh_on_rectangle_profile_produces_mirrored_triangles() -> None:
    profile = _rectangle_profile()
    options = Vessel3DViewOptions(split_enabled=True, split_angle_degrees=0.0)

    vertices, faces = section_cap_mesh(profile, options)

    # Two half-planes * 4 profile points.
    assert vertices.shape == (2 * len(profile), 3)
    # A 4-vertex profile triangulates into 2 triangles per half-plane -> 4.
    assert faces.shape == (4, 3)

    # Combined cap surface area equals 2 * (rectangle area in the r-z plane).
    total_area = _triangle_mesh_surface_area(vertices, faces)
    rectangle_area = 1.0 * 2.0
    assert total_area == pytest.approx(2.0 * rectangle_area, rel=1e-12)


def test_section_cap_mesh_returns_empty_for_degenerate_profile() -> None:
    # Fewer than three points -> nothing to triangulate.
    degenerate = (ProfilePoint(0.0, 0.0), ProfilePoint(1.0, 0.0))
    options = Vessel3DViewOptions(split_enabled=True)

    vertices, faces = section_cap_mesh(degenerate, options)

    assert vertices.shape == (0, 3)
    assert faces.shape == (0, 3)


# ---------------------------------------------------------------------------
# preview_angles
# ---------------------------------------------------------------------------


def test_preview_angles_full_revolution_spans_zero_to_two_pi_exclusive() -> None:
    angles = preview_angles(Vessel3DViewOptions())

    assert angles.shape == (DEFAULT_ANGULAR_SEGMENTS,)
    assert angles[0] == pytest.approx(0.0)
    # endpoint=False so the final sample sits just before 2*pi.
    assert angles[-1] == pytest.approx(
        2.0 * pi * (DEFAULT_ANGULAR_SEGMENTS - 1) / DEFAULT_ANGULAR_SEGMENTS
    )
    # Samples are strictly increasing with a uniform step.
    deltas = np.diff(angles)
    np.testing.assert_allclose(deltas, deltas[0], atol=1e-12)
    assert deltas[0] == pytest.approx(2.0 * pi / DEFAULT_ANGULAR_SEGMENTS)


def test_preview_angles_split_revolution_spans_half_turn_inclusive() -> None:
    options = Vessel3DViewOptions(split_enabled=True, split_angle_degrees=45.0)
    angles = preview_angles(options)

    half_count = (DEFAULT_ANGULAR_SEGMENTS // 2) + 1
    assert angles.shape == (half_count,)
    # First sample is the split angle; last sample is split_angle + pi.
    assert angles[0] == pytest.approx(options.normalized_split_angle_radians)
    assert angles[-1] == pytest.approx(options.normalized_split_angle_radians + pi)


# ---------------------------------------------------------------------------
# maybe_apply_section_cut
# ---------------------------------------------------------------------------


def test_maybe_apply_section_cut_is_no_op_when_split_disabled() -> None:
    profile = _rectangle_profile()
    vertices, faces = revolved_profile_mesh(profile, Vessel3DViewOptions())

    cut_vertices, cut_faces = maybe_apply_section_cut(
        (vertices, faces), Vessel3DViewOptions()
    )

    assert cut_vertices is vertices
    assert cut_faces is faces


def test_maybe_apply_section_cut_drops_hidden_half_when_split_enabled() -> None:
    profile = _rectangle_profile()
    full_vertices, full_faces = revolved_profile_mesh(profile, Vessel3DViewOptions())
    options = Vessel3DViewOptions(split_enabled=True, split_angle_degrees=0.0)

    _, visible_faces = maybe_apply_section_cut((full_vertices, full_faces), options)

    # Splitting at 0 degrees drops faces whose centroid lies on the -y side.
    # The full rotation is symmetric in y, so roughly half the faces survive.
    assert 0 < visible_faces.shape[0] < full_faces.shape[0]
    centroids = full_vertices[visible_faces].mean(axis=1)
    # Split normal for 0 deg is (0, 1, 0); kept faces have centroid.y >= ~0.
    assert (centroids[:, 1] >= -1e-9).all()


def test_maybe_apply_section_cut_returns_unchanged_for_empty_mesh() -> None:
    empty_vertices = np.empty((0, 3), dtype=np.float64)
    empty_faces = np.empty((0, 3), dtype=np.int32)
    options = Vessel3DViewOptions(split_enabled=True)

    vertices, faces = maybe_apply_section_cut((empty_vertices, empty_faces), options)

    assert vertices.shape == (0, 3)
    assert faces.shape == (0, 3)


# ---------------------------------------------------------------------------
# scene_bounds / make_mesh
# ---------------------------------------------------------------------------


def test_make_mesh_forwards_fields_and_stores_numpy_arrays() -> None:
    vertices = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    faces = np.array([[0, 1, 2]], dtype=np.int32)

    mesh = make_mesh(
        label="label",
        group_label="group",
        display_name="display",
        color_hex="#112233",
        alpha=0.75,
        vertices_faces=(vertices, faces),
    )

    assert isinstance(mesh, VesselSceneMesh)
    assert mesh.label == "label"
    assert mesh.group_label == "group"
    assert mesh.display_name == "display"
    assert mesh.color_hex == "#112233"
    assert mesh.alpha == pytest.approx(0.75)
    assert mesh.vertices is vertices
    assert mesh.faces is faces
    # ``polygons`` property fans out vertices by face indices.
    np.testing.assert_allclose(mesh.polygons, vertices[faces])


def test_scene_bounds_empty_returns_unit_cube_fallback() -> None:
    assert scene_bounds(()) == (-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)


def test_scene_bounds_skips_meshes_with_no_faces() -> None:
    populated_vertices = np.array([[2.0, 3.0, 4.0], [5.0, 6.0, 7.0]])
    populated_faces = np.array([[0, 1, 0]], dtype=np.int32)
    populated = make_mesh(
        label="p",
        group_label="g",
        display_name="d",
        color_hex="#fff",
        alpha=1.0,
        vertices_faces=(populated_vertices, populated_faces),
    )
    empty = make_mesh(
        label="e",
        group_label="g",
        display_name="d",
        color_hex="#000",
        alpha=1.0,
        vertices_faces=(
            np.array([[1000.0, 1000.0, 1000.0]]),
            np.empty((0, 3), dtype=np.int32),
        ),
    )

    bounds = scene_bounds((populated, empty))

    # Empty mesh's vertex must not contaminate bounds.
    assert bounds == (2.0, 5.0, 3.0, 6.0, 4.0, 7.0)


def test_scene_bounds_aggregates_across_multiple_meshes() -> None:
    mesh_a = make_mesh(
        label="a",
        group_label="g",
        display_name="d",
        color_hex="#fff",
        alpha=1.0,
        vertices_faces=(
            np.array([[-1.0, -1.0, -1.0], [0.0, 0.0, 0.0]]),
            np.array([[0, 1, 0]], dtype=np.int32),
        ),
    )
    mesh_b = make_mesh(
        label="b",
        group_label="g",
        display_name="d",
        color_hex="#fff",
        alpha=1.0,
        vertices_faces=(
            np.array([[2.0, 3.0, 4.0], [0.5, 0.5, 0.5]]),
            np.array([[0, 1, 0]], dtype=np.int32),
        ),
    )

    bounds = scene_bounds((mesh_a, mesh_b))

    assert bounds == (-1.0, 2.0, -1.0, 3.0, -1.0, 4.0)
