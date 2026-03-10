import pytest

from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    VesselDrafterLayout,
)


def test_defaults_match_requested_vessel_stackup() -> None:
    layout = DEFAULT_VESSEL_DRAFTER_LAYOUT

    assert layout.inner_diameter_in == pytest.approx(50.0)
    assert layout.glass_depth_in == pytest.approx(14.0)
    assert layout.plenum_height_in == pytest.approx(14.0)
    assert layout.head_depth_in == pytest.approx(12.5)
    assert [layer.name for layer in layout.layers] == [
        "glass_bath",
        "hot_face_refractory",
        "ifb",
        "duraboard",
        "steel_shell",
    ]


def test_invalid_dimensions_raise_value_error() -> None:
    with pytest.raises(ValueError):
        VesselDrafterLayout(inner_diameter_in=0.0)

    with pytest.raises(ValueError):
        VesselDrafterLayout(plenum_height_in=0.0)

    with pytest.raises(ValueError):
        VesselDrafterLayout(electrode_insertion_into_inner_circle_in=30.0)
