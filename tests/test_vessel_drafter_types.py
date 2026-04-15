"""Tests for the vessel drafter dataclass types."""

from __future__ import annotations

import pytest

from programmatic_drafting.models.vessel_drafter import VesselDrafterLayout
from programmatic_drafting.models.vessel_drafter_types import (
    MaterialLayer,
    RadialBand,
    VesselElectrodePlacement,
    VesselLidPort,
    VesselSidePort,
)
from programmatic_drafting.models.vessel_materials import (
    DEFAULT_VESSEL_MATERIALS_BY_NAME,
)


def test_material_layer_exposes_material_properties() -> None:
    layer = MaterialLayer(
        DEFAULT_VESSEL_MATERIALS_BY_NAME["steel_shell"],
        thickness_in=0.5,
    )

    assert layer.name == "steel_shell"
    assert layer.display_name == "Steel Shell"
    assert layer.thickness_in == 0.5
    assert layer.category == layer.properties.category


def test_radial_band_label_matches_name() -> None:
    band = RadialBand(
        name="ifb",
        color_hex="#abcdef",
        inner_radius_in=10.0,
        outer_radius_in=14.5,
    )

    assert band.label == "ifb"
    assert band.inner_offset_in == 10.0


def test_vessel_electrode_placement_is_frozen() -> None:
    placement = VesselElectrodePlacement(
        index=1,
        angle_degrees=0.0,
        angle_radians=0.0,
        inner_tip_radius_in=11.0,
        outer_tip_radius_in=61.0,
        diameter_in=2.0,
    )

    with pytest.raises(AttributeError):
        placement.index = 2  # type: ignore[misc]


def test_vessel_side_port_computes_centerline_height() -> None:
    layout = VesselDrafterLayout()
    port = VesselSidePort(
        clock_angle_degrees=90.0,
        diameter_in=3.0,
        height_above_glass_surface_in=4.0,
    )

    assert port.centerline_height_in(layout) == layout.glass_depth_in + 4.0


def test_vessel_side_port_rejects_negative_height() -> None:
    with pytest.raises(ValueError):
        VesselSidePort(
            clock_angle_degrees=0.0,
            diameter_in=3.0,
            height_above_glass_surface_in=-1.0,
        )


def test_vessel_lid_port_rejects_non_positive_diameter() -> None:
    with pytest.raises(ValueError):
        VesselLidPort(
            clock_angle_degrees=0.0,
            diameter_in=0.0,
            radial_distance_from_center_in=5.0,
        )
