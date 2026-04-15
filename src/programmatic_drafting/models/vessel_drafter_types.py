"""Dataclass types used by the vessel drafter layout.

Each type in this module is a frozen, validated dataclass that represents
one piece of vessel geometry: a material layer, a radial band, an electrode
placement, or a port. The aggregate :class:`VesselDrafterLayout` lives in
``vessel_drafter`` and composes these types.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from programmatic_drafting.contracts import (
    require_finite,
    require_nonnegative,
    require_positive,
)
from programmatic_drafting.models.ports import PortMixin
from programmatic_drafting.models.vessel_materials import MaterialProperties

if TYPE_CHECKING:
    from programmatic_drafting.models.vessel_drafter import VesselDrafterLayout


@dataclass(frozen=True)
class MaterialLayer:
    properties: MaterialProperties
    thickness_in: float

    @property
    def name(self) -> str:
        return self.properties.name

    @property
    def display_name(self) -> str:
        return self.properties.display_name

    @property
    def color_hex(self) -> str:
        return self.properties.color_hex

    @property
    def category(self) -> str:
        return self.properties.category

    @property
    def density_lb_per_ft3(self) -> float:
        return self.properties.density_lb_per_ft3

    @property
    def thermal_conductivity_w_per_mk(self) -> float:
        return self.properties.thermal_conductivity_w_per_mk

    @property
    def thermal_expansion_um_per_m_c(self) -> float:
        return self.properties.thermal_expansion_um_per_m_c

    @property
    def preview_alpha(self) -> float:
        return self.properties.preview_alpha


@dataclass(frozen=True)
class RadialBand:
    name: str
    color_hex: str
    inner_radius_in: float
    outer_radius_in: float

    @property
    def label(self) -> str:
        return self.name

    @property
    def inner_offset_in(self) -> float:
        return self.inner_radius_in


@dataclass(frozen=True)
class VesselElectrodePlacement:
    index: int
    angle_degrees: float
    angle_radians: float
    inner_tip_radius_in: float
    outer_tip_radius_in: float
    diameter_in: float


@dataclass(frozen=True)
class VesselSidePort(PortMixin):
    clock_angle_degrees: float
    diameter_in: float
    height_above_glass_surface_in: float

    def __post_init__(self) -> None:
        require_finite("clock_angle_degrees", self.clock_angle_degrees)
        require_positive("diameter_in", self.diameter_in)
        require_nonnegative(
            "height_above_glass_surface_in",
            self.height_above_glass_surface_in,
        )

    def centerline_height_in(self, layout: VesselDrafterLayout) -> float:
        return layout.glass_depth_in + self.height_above_glass_surface_in


@dataclass(frozen=True)
class VesselLidPort(PortMixin):
    clock_angle_degrees: float
    diameter_in: float
    radial_distance_from_center_in: float

    def __post_init__(self) -> None:
        require_finite("clock_angle_degrees", self.clock_angle_degrees)
        require_positive("diameter_in", self.diameter_in)
        require_nonnegative(
            "radial_distance_from_center_in",
            self.radial_distance_from_center_in,
        )
