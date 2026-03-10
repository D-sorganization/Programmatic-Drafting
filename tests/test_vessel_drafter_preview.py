import pytest

from programmatic_drafting.models.vessel_drafter import DEFAULT_VESSEL_DRAFTER_LAYOUT
from programmatic_drafting.preview.vessel_drafter_preview import (
    build_cross_section_preview,
    build_plan_preview,
)


def test_cross_section_preview_matches_expected_envelope() -> None:
    preview = build_cross_section_preview(DEFAULT_VESSEL_DRAFTER_LAYOUT)

    assert preview.inner_radius_in == pytest.approx(25.0)
    assert preview.outer_radius_in == pytest.approx(37.0)
    assert preview.straight_shell_height_in == pytest.approx(28.0)
    assert preview.inner_head_depth_in == pytest.approx(12.5)
    assert preview.outer_head_depth_in == pytest.approx(18.5)
    assert preview.glass_height_in == pytest.approx(14.0)
    assert preview.plenum_height_in == pytest.approx(14.0)
    assert [band.label for band in preview.bands] == [
        "glass_bath",
        "hot_face_refractory",
        "ifb",
        "duraboard",
        "steel_shell",
    ]


def test_plan_preview_has_three_radial_electrodes() -> None:
    preview = build_plan_preview(DEFAULT_VESSEL_DRAFTER_LAYOUT)

    assert preview.outer_radius_in == pytest.approx(37.0)
    assert [item.angle_degrees for item in preview.electrodes] == pytest.approx(
        [0.0, 120.0, 240.0]
    )
    assert preview.electrodes[0].outer_tip_radius_in == pytest.approx(61.0)
