"""Revolved profile mesh tests for the vessel 3D scene."""

from __future__ import annotations

from math import pi

import numpy as np
import pytest
from _vessel_drafter_scene_mesh_helpers import (
    rectangle_profile,
    triangle_mesh_surface_area,
)

from programmatic_drafting.preview._vessel_drafter_scene_common import (
    DEFAULT_ANGULAR_SEGMENTS,
)
from programmatic_drafting.preview._vessel_drafter_scene_revolution import (
    revolved_profile_mesh,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)
from programmatic_drafting.projects.vessel_drafter_profiles import ProfilePoint


def test_revolved_profile_mesh_full_rotation_counts_match_schema() -> None:
    profile = rectangle_profile()

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
    profile = rectangle_profile()

    vertices, _ = revolved_profile_mesh(profile, Vessel3DViewOptions())

    assert vertices[:, 0].min() == pytest.approx(-1.0, abs=1e-12)
    assert vertices[:, 0].max() == pytest.approx(1.0, abs=1e-12)
    assert vertices[:, 1].min() == pytest.approx(-1.0, abs=1e-12)
    assert vertices[:, 1].max() == pytest.approx(1.0, abs=1e-12)
    assert vertices[:, 2].min() == pytest.approx(0.0, abs=1e-12)
    assert vertices[:, 2].max() == pytest.approx(2.0, abs=1e-12)


def test_revolved_profile_mesh_surface_area_matches_inscribed_prism() -> None:
    profile = rectangle_profile()

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

    observed_area = triangle_mesh_surface_area(vertices, faces)
    assert observed_area == pytest.approx(expected_area, rel=1e-12)


def test_revolved_profile_mesh_split_view_uses_half_revolution_counts() -> None:
    profile = rectangle_profile()
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
    assert triangle_mesh_surface_area(vertices, faces) > 0.0
    assert vertices[:, 2].min() == pytest.approx(0.0, abs=1e-12)
    assert vertices[:, 2].max() == pytest.approx(2.0, abs=1e-12)
