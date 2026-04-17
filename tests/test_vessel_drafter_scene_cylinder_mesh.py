"""Cylinder mesh construction tests for the vessel 3D scene."""

from __future__ import annotations

from math import pi

import numpy as np
import pytest
from _vessel_drafter_scene_mesh_helpers import triangle_mesh_surface_area

from programmatic_drafting.preview._vessel_drafter_scene_common import (
    DEFAULT_ELECTRODE_SEGMENTS,
)
from programmatic_drafting.preview._vessel_drafter_scene_cylinder import (
    cylinder_mesh,
)


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

    observed = triangle_mesh_surface_area(vertices, faces)
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
