"""Dedicated tests for the ear-clipping triangulator used by the vessel scene.

Issue #21 calls out the triangulation helper as untested. The routine lives in
``programmatic_drafting.preview._vessel_drafter_scene_section`` (re-exported
through the ``vessel_drafter_scene`` facade) and is exercised here against a
variety of convex and concave polygons with known-good expected outputs.
"""

from __future__ import annotations

import pytest

from programmatic_drafting.preview._vessel_drafter_scene_section import (
    _fan_triangulation,
    _signed_area,
    _triangulate_profile_loop,
)
from programmatic_drafting.projects.vessel_drafter_profiles import ProfilePoint


def _total_triangle_area(
    triangles: tuple[tuple[int, int, int], ...],
    profile: tuple[ProfilePoint, ...],
) -> float:
    """Sum of absolute triangle areas produced by the triangulator."""
    total = 0.0
    for index_a, index_b, index_c in triangles:
        point_a = profile[index_a]
        point_b = profile[index_b]
        point_c = profile[index_c]
        cross = (point_b.x_in - point_a.x_in) * (point_c.z_in - point_a.z_in) - (
            point_c.x_in - point_a.x_in
        ) * (point_b.z_in - point_a.z_in)
        total += abs(cross) * 0.5
    return total


def _polygon_area(profile: tuple[ProfilePoint, ...]) -> float:
    """Shoelace area (unsigned) for a simple polygon."""
    total = 0.0
    for index, point in enumerate(profile):
        following = profile[(index + 1) % len(profile)]
        total += (point.x_in * following.z_in) - (following.x_in * point.z_in)
    return abs(total) * 0.5


def test_triangulate_profile_loop_returns_empty_for_fewer_than_three_points() -> None:
    assert _triangulate_profile_loop(()) == ()
    assert _triangulate_profile_loop((ProfilePoint(0.0, 0.0),)) == ()
    assert (
        _triangulate_profile_loop(
            (ProfilePoint(0.0, 0.0), ProfilePoint(1.0, 0.0)),
        )
        == ()
    )


def test_triangulate_profile_loop_on_unit_triangle_returns_single_fan() -> None:
    triangle = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(1.0, 0.0),
        ProfilePoint(0.0, 1.0),
    )

    triangles = _triangulate_profile_loop(triangle)

    assert triangles == ((0, 1, 2),)
    assert _total_triangle_area(triangles, triangle) == pytest.approx(0.5)


def test_triangulate_profile_loop_square_produces_two_triangles_covering_area() -> None:
    square = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(2.0, 0.0),
        ProfilePoint(2.0, 2.0),
        ProfilePoint(0.0, 2.0),
    )

    triangles = _triangulate_profile_loop(square)

    assert len(triangles) == 2
    # Each returned triple is a valid index triple in the polygon.
    for triple in triangles:
        assert len(set(triple)) == 3
        for index in triple:
            assert 0 <= index < len(square)
    # Combined triangle area exactly covers the square.
    assert _total_triangle_area(triangles, square) == pytest.approx(4.0)


def test_triangulate_profile_loop_concave_arrow_matches_known_output() -> None:
    # Same concave polygon used in ``test_vessel_drafter_scene_section`` to
    # pin the documented ear-clipping order.
    arrow = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(2.0, 0.0),
        ProfilePoint(2.0, 1.0),
        ProfilePoint(1.0, 0.5),
        ProfilePoint(0.0, 1.0),
    )

    triangles = _triangulate_profile_loop(arrow)

    assert triangles == ((1, 2, 3), (0, 1, 3), (0, 3, 4))
    # Triangulation always yields n - 2 triangles for a simple n-gon.
    assert len(triangles) == len(arrow) - 2
    # Triangles partition the polygon so their summed area equals the polygon
    # area computed independently via the shoelace formula.
    assert _total_triangle_area(triangles, arrow) == pytest.approx(_polygon_area(arrow))


def test_triangulate_profile_loop_handles_clockwise_polygon() -> None:
    # The same square, but wound clockwise. Ear-clipping should still succeed
    # and produce a covering triangulation.
    clockwise_square = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(0.0, 2.0),
        ProfilePoint(2.0, 2.0),
        ProfilePoint(2.0, 0.0),
    )

    triangles = _triangulate_profile_loop(clockwise_square)

    assert len(triangles) == 2
    assert _total_triangle_area(triangles, clockwise_square) == pytest.approx(4.0)


def test_triangulate_profile_loop_on_concave_hex_covers_area_exactly() -> None:
    # A concave hexagon (index 3 is pushed inward) — a classic ear-clipping
    # stress case that cannot be fan-triangulated from a single vertex.
    concave_hex = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(4.0, 0.0),
        ProfilePoint(4.0, 2.0),
        ProfilePoint(2.0, 1.0),
        ProfilePoint(0.0, 2.0),
        ProfilePoint(-1.0, 1.0),
    )

    triangles = _triangulate_profile_loop(concave_hex)

    # Simple polygon with n vertices must yield n - 2 triangles.
    assert len(triangles) == len(concave_hex) - 2
    for triple in triangles:
        assert len(set(triple)) == 3
        for index in triple:
            assert 0 <= index < len(concave_hex)
    assert _total_triangle_area(triangles, concave_hex) == pytest.approx(
        _polygon_area(concave_hex)
    )


def test_triangulate_profile_loop_degenerate_collinear_points_yields_zero_area() -> (
    None
):
    # Three collinear points — degenerate but not crashing.
    collinear = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(1.0, 0.0),
        ProfilePoint(2.0, 0.0),
    )

    triangles = _triangulate_profile_loop(collinear)

    # The algorithm still emits a single index triple (a degenerate triangle).
    assert triangles == ((0, 1, 2),)
    assert _total_triangle_area(triangles, collinear) == pytest.approx(0.0)


def test_signed_area_matches_shoelace_sign_and_magnitude() -> None:
    import numpy as np

    ccw_square = np.array(
        [[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0]],
        dtype=np.float64,
    )
    cw_square = ccw_square[::-1].copy()

    assert _signed_area(ccw_square) == pytest.approx(4.0)
    assert _signed_area(cw_square) == pytest.approx(-4.0)


def test_fan_triangulation_produces_expected_triples() -> None:
    assert _fan_triangulation([]) == ()
    assert _fan_triangulation([0, 1]) == ()
    assert _fan_triangulation([0, 1, 2]) == ((0, 1, 2),)
    assert _fan_triangulation([0, 1, 2, 3]) == ((0, 1, 2), (0, 2, 3))
    assert _fan_triangulation([5, 6, 7, 8, 9]) == (
        (5, 6, 7),
        (5, 7, 8),
        (5, 8, 9),
    )
