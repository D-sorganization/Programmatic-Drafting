"""Unit tests for ``programmatic_drafting.projects.vessel_drafter_profiles``.

These cover the elliptical-head math and boundary-loop builders used by both
the preview scene and the STEP export pipeline. They target issue #21 which
flagged these helpers as untested.
"""

from __future__ import annotations

from math import cos, isclose, pi

import pytest

from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    VesselDrafterLayout,
)
from programmatic_drafting.projects.vessel_drafter_profiles import (
    HEAD_SAMPLE_COUNT,
    ProfilePoint,
    ShellBandProfile,
    build_band_boundary_loops,
    build_bottom_head_curve,
    build_cavity_boundary_half,
    build_full_boundary_loop,
    build_glass_boundary_half,
    build_plenum_boundary_half,
    build_shell_band_profiles,
    build_shell_boundary_half,
    build_top_head_curve,
)


def test_profile_point_mirror_negates_x_and_preserves_z() -> None:
    original = ProfilePoint(x_in=3.5, z_in=-2.25)

    mirrored = original.mirrored_x()

    assert mirrored.x_in == pytest.approx(-3.5)
    assert mirrored.z_in == pytest.approx(-2.25)
    # Mirror is an involution on x.
    assert mirrored.mirrored_x() == original


def test_build_shell_band_profiles_offsets_are_contiguous_and_cumulative() -> None:
    profiles = build_shell_band_profiles()

    assert len(profiles) == len(DEFAULT_VESSEL_DRAFTER_LAYOUT.shell_bands)
    assert profiles[0].inner_offset_in == pytest.approx(0.0)

    running = 0.0
    for profile in profiles:
        band = profile.band
        thickness = band.outer_radius_in - band.inner_radius_in
        assert profile.inner_offset_in == pytest.approx(running)
        running += thickness
        assert profile.outer_offset_in == pytest.approx(running)
        assert isinstance(profile, ShellBandProfile)

    last = profiles[-1]
    total_thickness = (
        DEFAULT_VESSEL_DRAFTER_LAYOUT.outer_radius_in
        - DEFAULT_VESSEL_DRAFTER_LAYOUT.inner_radius_in
    )
    assert last.outer_offset_in == pytest.approx(total_thickness)


def test_top_head_curve_endpoints_match_springline_and_apex() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT
    curve = build_top_head_curve(layout, offset_in=0.0)

    assert len(curve) == HEAD_SAMPLE_COUNT + 1
    # theta=0 -> (radius, springline)
    assert curve[0].x_in == pytest.approx(layout.inner_radius_in)
    assert curve[0].z_in == pytest.approx(layout.straight_shell_height_in)
    # theta=pi/2 -> (0, springline + head_depth)
    assert curve[-1].x_in == pytest.approx(0.0, abs=1e-9)
    assert curve[-1].z_in == pytest.approx(
        layout.straight_shell_height_in + layout.head_depth_in
    )


def test_top_head_curve_midpoint_lies_on_ellipse() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT
    curve = build_top_head_curve(layout, offset_in=0.0)

    middle = curve[HEAD_SAMPLE_COUNT // 2]
    # Ellipse equation: (x/a)^2 + ((z - z0)/b)^2 == 1 for offset=0.
    a = layout.inner_radius_in
    b = layout.head_depth_in
    lhs = (middle.x_in / a) ** 2 + (
        (middle.z_in - layout.straight_shell_height_in) / b
    ) ** 2
    assert lhs == pytest.approx(1.0, abs=1e-9)


def test_top_head_curve_offset_pushes_points_outward_along_normal() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT
    inner = build_top_head_curve(layout, offset_in=0.0)
    outer = build_top_head_curve(layout, offset_in=1.5)

    # Apex moves straight up in z by exactly the offset.
    assert outer[-1].x_in == pytest.approx(0.0, abs=1e-9)
    assert outer[-1].z_in == pytest.approx(inner[-1].z_in + 1.5)
    # Springline side moves outward in x by exactly the offset.
    assert outer[0].x_in == pytest.approx(inner[0].x_in + 1.5)
    assert outer[0].z_in == pytest.approx(inner[0].z_in)

    # Every offset point is farther from the ellipse center than its inner twin.
    for inner_point, outer_point in zip(inner, outer, strict=True):
        inner_radial = (
            (inner_point.x_in) ** 2
            + (inner_point.z_in - layout.straight_shell_height_in) ** 2
        ) ** 0.5
        outer_radial = (
            (outer_point.x_in) ** 2
            + (outer_point.z_in - layout.straight_shell_height_in) ** 2
        ) ** 0.5
        assert outer_radial > inner_radial


def test_bottom_head_curve_is_mirror_of_top_about_z_zero() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT
    top = build_top_head_curve(layout, offset_in=0.0)
    bottom = build_bottom_head_curve(layout, offset_in=0.0)

    assert len(bottom) == len(top)
    # The bottom curve starts at the apex (below z=0) and ends at the
    # springline at z == 0 where it meets the cylindrical shell.
    assert bottom[0].x_in == pytest.approx(0.0, abs=1e-9)
    assert bottom[0].z_in == pytest.approx(-layout.head_depth_in)
    assert bottom[-1].x_in == pytest.approx(layout.inner_radius_in)
    assert bottom[-1].z_in == pytest.approx(0.0, abs=1e-9)


def test_sample_count_parameter_controls_curve_length() -> None:
    sparse = build_top_head_curve(sample_count=4)
    dense = build_top_head_curve(sample_count=96)

    assert len(sparse) == 5
    assert len(dense) == 97
    # First/last anchors agree regardless of sampling density.
    assert sparse[0].x_in == pytest.approx(dense[0].x_in)
    assert sparse[0].z_in == pytest.approx(dense[0].z_in)
    assert sparse[-1].x_in == pytest.approx(dense[-1].x_in, abs=1e-9)
    assert sparse[-1].z_in == pytest.approx(dense[-1].z_in)


def test_shell_boundary_half_joins_bottom_springline_and_top() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT
    half = build_shell_boundary_half(layout, offset_in=0.0)

    expected_length = (
        (HEAD_SAMPLE_COUNT + 1)  # full bottom curve
        + 1  # explicit springline vertex
        + HEAD_SAMPLE_COUNT  # top curve minus duplicate first sample
    )
    assert len(half) == expected_length
    # Starts on the bottom apex, ends on the top apex.
    assert half[0].z_in == pytest.approx(-layout.head_depth_in)
    assert half[-1].x_in == pytest.approx(0.0, abs=1e-9)
    assert half[-1].z_in == pytest.approx(
        layout.straight_shell_height_in + layout.head_depth_in
    )
    # Explicit springline vertex is exactly at (radius, straight_shell_height).
    springline_vertex = half[HEAD_SAMPLE_COUNT + 1]
    assert springline_vertex.x_in == pytest.approx(layout.inner_radius_in)
    assert springline_vertex.z_in == pytest.approx(layout.straight_shell_height_in)


def test_cavity_glass_and_plenum_halves_have_expected_corners() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT

    cavity = build_cavity_boundary_half(layout)
    glass = build_glass_boundary_half(layout)
    plenum = build_plenum_boundary_half(layout)

    # Cavity axis + radial + springline + top head samples (minus duplicate).
    assert len(cavity) == 3 + HEAD_SAMPLE_COUNT
    assert cavity[0] == ProfilePoint(0.0, 0.0)
    assert cavity[1] == ProfilePoint(layout.inner_radius_in, 0.0)
    assert cavity[2] == ProfilePoint(
        layout.inner_radius_in, layout.straight_shell_height_in
    )

    assert glass == (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(layout.inner_radius_in, 0.0),
        ProfilePoint(layout.inner_radius_in, layout.glass_depth_in),
        ProfilePoint(0.0, layout.glass_depth_in),
    )

    assert plenum == (
        ProfilePoint(0.0, layout.glass_depth_in),
        ProfilePoint(layout.inner_radius_in, layout.glass_depth_in),
        ProfilePoint(layout.inner_radius_in, layout.straight_shell_height_in),
        ProfilePoint(0.0, layout.straight_shell_height_in),
    )


def test_full_boundary_loop_mirrors_half_without_duplicating_endpoints() -> None:
    half = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(2.0, 0.0),
        ProfilePoint(2.0, 3.0),
        ProfilePoint(0.0, 3.0),
    )

    loop = build_full_boundary_loop(half)

    # For a half of length N, the mirrored loop has length N + (N - 1) since
    # the last vertex (on the axis) is not duplicated via the mirror.
    assert len(loop) == len(half) + (len(half) - 1)
    assert loop[: len(half)] == half
    mirrored_tail = loop[len(half) :]
    # Tail starts with mirror of the second-to-last half point and ends with
    # mirror of the first half point.
    assert mirrored_tail[0] == ProfilePoint(-2.0, 3.0)
    assert mirrored_tail[-1] == ProfilePoint(0.0, 0.0)


def test_full_boundary_loop_on_cavity_half_has_finite_area() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT
    loop = build_full_boundary_loop(build_cavity_boundary_half(layout))

    # Shoelace formula for a closed polygon; expect a non-degenerate area at
    # least as large as the bare straight-shell rectangle across the full
    # diameter.
    signed_area = 0.0
    for index, point in enumerate(loop):
        next_point = loop[(index + 1) % len(loop)]
        signed_area += (point.x_in * next_point.z_in) - (next_point.x_in * point.z_in)
    area = 0.5 * signed_area
    minimum_area = 2.0 * layout.inner_radius_in * layout.straight_shell_height_in
    assert abs(area) > minimum_area


def test_build_band_boundary_loops_shares_cavity_loop_for_innermost_band() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT
    cavity_loop = build_full_boundary_loop(build_cavity_boundary_half(layout))
    loops = build_band_boundary_loops(layout)

    assert len(loops) == len(layout.shell_bands)

    innermost_profile, _outer_loop, innermost_inner_loop = loops[0]
    assert innermost_profile.inner_offset_in == pytest.approx(0.0)
    # The innermost band reuses the cavity boundary loop exactly.
    assert innermost_inner_loop == cavity_loop

    # Every outer loop of band N should equal the inner loop of band N+1 so
    # adjacent bands share a watertight seam.
    for current, following in zip(loops, loops[1:], strict=False):
        _current_profile, current_outer, _current_inner = current
        _following_profile, _following_outer, following_inner = following
        assert current_outer == following_inner


def test_custom_layout_scales_apex_height_linearly_with_head_depth() -> None:
    layout = VesselDrafterLayout(head_depth_in=5.0)
    curve = build_top_head_curve(layout, offset_in=0.0)

    apex_z = curve[-1].z_in
    springline_z = layout.straight_shell_height_in
    assert isclose(apex_z - springline_z, 5.0, rel_tol=0.0, abs_tol=1e-9)
    # Midpoint sample should sit on the analytic ellipse at theta=pi/4.
    index_quarter = HEAD_SAMPLE_COUNT // 2
    theta_quarter = (pi * 0.5) * (index_quarter / HEAD_SAMPLE_COUNT)
    expected_x = layout.inner_radius_in * cos(theta_quarter)
    assert curve[index_quarter].x_in == pytest.approx(expected_x)
