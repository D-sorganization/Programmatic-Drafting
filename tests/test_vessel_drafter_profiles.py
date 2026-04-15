import pytest

from programmatic_drafting.models.vessel_drafter import DEFAULT_VESSEL_DRAFTER_LAYOUT
from programmatic_drafting.projects.vessel_drafter_profiles import (
    ProfilePoint,
    build_band_boundary_loops,
    build_bottom_head_curve,
    build_full_boundary_loop,
    build_shell_band_profiles,
    build_top_head_curve,
)


def test_top_head_curve_starts_at_springline_and_ends_at_apex() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT

    points = build_top_head_curve(layout, sample_count=4)

    assert len(points) == 5
    assert points[0].x_in == pytest.approx(layout.inner_radius_in)
    assert points[0].z_in == pytest.approx(layout.straight_shell_height_in)
    assert points[-1].x_in == pytest.approx(0.0)
    assert points[-1].z_in == pytest.approx(
        layout.straight_shell_height_in + layout.head_depth_in
    )


def test_bottom_head_curve_runs_toward_the_lower_apex() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT

    points = build_bottom_head_curve(layout, sample_count=4)

    assert len(points) == 5
    assert points[0].x_in == pytest.approx(0.0)
    assert points[0].z_in == pytest.approx(-layout.head_depth_in)
    assert points[-1].x_in == pytest.approx(layout.inner_radius_in)
    assert points[-1].z_in == pytest.approx(0.0)


def test_full_boundary_loop_mirrors_half_without_duplication() -> None:
    half_boundary = (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(1.0, 1.0),
        ProfilePoint(2.0, 2.0),
        ProfilePoint(3.0, 3.0),
    )

    full_boundary = build_full_boundary_loop(half_boundary)

    assert len(full_boundary) == (len(half_boundary) * 2) - 1
    assert full_boundary[: len(half_boundary)] == half_boundary
    assert full_boundary[len(half_boundary) :] == (
        ProfilePoint(-2.0, 2.0),
        ProfilePoint(-1.0, 1.0),
        ProfilePoint(-0.0, 0.0),
    )


def test_band_boundary_loops_mirror_each_shell_band() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT

    profiles = build_shell_band_profiles(layout)
    loops = build_band_boundary_loops(layout)

    assert len(loops) == len(profiles) == 4
    assert [profile.band.label for profile, _, _ in loops] == [
        "hot_face_refractory",
        "ifb",
        "duraboard",
        "steel_shell",
    ]

    cavity_loop = build_full_boundary_loop(
        (
            ProfilePoint(0.0, 0.0),
            ProfilePoint(layout.inner_radius_in, 0.0),
            ProfilePoint(layout.inner_radius_in, layout.straight_shell_height_in),
            *build_top_head_curve(layout, 0.0)[1:],
        )
    )

    first_profile, first_outer_loop, first_inner_loop = loops[0]
    assert first_profile.inner_offset_in == pytest.approx(0.0)
    assert first_inner_loop == cavity_loop
    assert first_outer_loop[0].x_in == pytest.approx(0.0)
    assert first_outer_loop[-1].x_in == pytest.approx(0.0)
    assert max(point.x_in for point in first_outer_loop) == pytest.approx(
        layout.inner_radius_in
        + first_profile.band.outer_radius_in
        - first_profile.band.inner_radius_in
    )

    second_profile, second_outer_loop, second_inner_loop = loops[1]
    assert second_profile.inner_offset_in == pytest.approx(
        first_profile.band.outer_radius_in - first_profile.band.inner_radius_in
    )
    assert second_inner_loop[0].x_in == pytest.approx(0.0)
    assert second_outer_loop[0].x_in == pytest.approx(0.0)
    assert max(point.x_in for point in second_outer_loop) == pytest.approx(
        layout.inner_radius_in + second_profile.outer_offset_in
    )
