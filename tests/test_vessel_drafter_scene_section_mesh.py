"""Section cut and cap mesh tests for the vessel 3D scene."""

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
from programmatic_drafting.preview._vessel_drafter_scene_section import (
    maybe_apply_section_cut,
    preview_angles,
    section_cap_mesh,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)
from programmatic_drafting.projects.vessel_drafter_profiles import ProfilePoint


def test_section_cap_mesh_on_rectangle_profile_produces_mirrored_triangles() -> None:
    profile = rectangle_profile()
    options = Vessel3DViewOptions(split_enabled=True, split_angle_degrees=0.0)

    vertices, faces = section_cap_mesh(profile, options)

    # Two half-planes * 4 profile points.
    assert vertices.shape == (2 * len(profile), 3)
    # A 4-vertex profile triangulates into 2 triangles per half-plane -> 4.
    assert faces.shape == (4, 3)

    # Combined cap surface area equals 2 * (rectangle area in the r-z plane).
    total_area = triangle_mesh_surface_area(vertices, faces)
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
    profile = rectangle_profile()
    vertices, faces = revolved_profile_mesh(profile, Vessel3DViewOptions())

    cut_vertices, cut_faces = maybe_apply_section_cut(
        (vertices, faces), Vessel3DViewOptions()
    )

    assert cut_vertices is vertices
    assert cut_faces is faces


def test_maybe_apply_section_cut_drops_hidden_half_when_split_enabled() -> None:
    profile = rectangle_profile()
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
