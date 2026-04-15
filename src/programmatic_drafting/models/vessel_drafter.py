"""Validated defaults and geometry helpers for the vessel drafter tool.

The dataclass types (``MaterialLayer``, ``RadialBand``,
``VesselElectrodePlacement``, ``VesselSidePort``, ``VesselLidPort``) are
defined in :mod:`programmatic_drafting.models.vessel_drafter_types` and the
manifest builders live in
:mod:`programmatic_drafting.models.vessel_drafter_manifest`. Both are
re-exported from this module for backwards compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import radians
from typing import Any

from programmatic_drafting.constants import MM_PER_INCH
from programmatic_drafting.contracts import (
    require_fraction,
    require_integer_at_least,
    require_less_or_equal,
    require_nonnegative,
    require_positive,
)
from programmatic_drafting.models.vessel_drafter_manifest import (
    _build_drafting_assumptions_manifest,
    _build_electrodes_manifest,
    _build_glass_bath_manifest,
    _build_lid_port_manifest,
    _build_material_manifest,
    _build_ports_manifest,
    _build_shell_materials_manifest,
    _build_side_port_manifest,
    _build_vessel_manifest,
    build_vessel_drafter_manifest,
)
from programmatic_drafting.models.vessel_drafter_types import (
    MaterialLayer,
    RadialBand,
    VesselElectrodePlacement,
    VesselLidPort,
    VesselSidePort,
)
from programmatic_drafting.models.vessel_materials import (
    DEFAULT_VESSEL_MATERIALS_BY_NAME,
    MaterialProperties,
)

__all__ = [
    "DEFAULT_VESSEL_DRAFTER_LAYOUT",
    "MaterialLayer",
    "RadialBand",
    "VesselDrafterLayout",
    "VesselElectrodePlacement",
    "VesselLidPort",
    "VesselSidePort",
    "_build_drafting_assumptions_manifest",
    "_build_electrodes_manifest",
    "_build_glass_bath_manifest",
    "_build_lid_port_manifest",
    "_build_material_manifest",
    "_build_ports_manifest",
    "_build_shell_materials_manifest",
    "_build_side_port_manifest",
    "_build_vessel_manifest",
    "build_vessel_drafter_manifest",
]


@dataclass(frozen=True)
class VesselDrafterLayout:
    inner_diameter_in: float = 50.0
    glass_depth_in: float = 14.0
    plenum_height_in: float = 14.0
    head_depth_in: float = 12.5
    hot_face_thickness_in: float = 6.0
    ifb_thickness_in: float = 4.5
    duraboard_thickness_in: float = 1.0
    steel_thickness_in: float = 0.5
    electrode_count: int = 3
    electrode_diameter_in: float = 2.0
    electrode_insertion_into_inner_circle_in: float = 14.0
    electrode_extension_past_inner_circle_in: float = 36.0
    electrode_centerline_height_fraction: float = 0.5
    side_ports: tuple[VesselSidePort, ...] = ()
    lid_ports: tuple[VesselLidPort, ...] = ()

    def __post_init__(self) -> None:
        require_positive("inner_diameter_in", self.inner_diameter_in)
        require_positive("glass_depth_in", self.glass_depth_in)
        require_positive("plenum_height_in", self.plenum_height_in)
        require_positive("head_depth_in", self.head_depth_in)
        require_positive("hot_face_thickness_in", self.hot_face_thickness_in)
        require_positive("ifb_thickness_in", self.ifb_thickness_in)
        require_positive("duraboard_thickness_in", self.duraboard_thickness_in)
        require_positive("steel_thickness_in", self.steel_thickness_in)
        require_integer_at_least("electrode_count", self.electrode_count, 1)
        require_positive("electrode_diameter_in", self.electrode_diameter_in)
        require_positive(
            "electrode_insertion_into_inner_circle_in",
            self.electrode_insertion_into_inner_circle_in,
        )
        require_positive(
            "electrode_extension_past_inner_circle_in",
            self.electrode_extension_past_inner_circle_in,
        )
        require_fraction(
            "electrode_centerline_height_fraction",
            self.electrode_centerline_height_fraction,
        )
        require_less_or_equal(
            "electrode_insertion_into_inner_circle_in",
            self.electrode_insertion_into_inner_circle_in,
            self.inner_radius_in,
        )
        self._validate_side_ports()
        self._validate_lid_ports()

    @property
    def inner_radius_in(self) -> float:
        return self.inner_diameter_in * 0.5

    @property
    def straight_shell_height_in(self) -> float:
        return self.glass_depth_in + self.plenum_height_in

    @property
    def total_shell_thickness_in(self) -> float:
        return sum(layer.thickness_in for layer in self.layers[1:])

    @property
    def outer_radius_in(self) -> float:
        return self.shell_bands[-1].outer_radius_in

    @property
    def outer_diameter_in(self) -> float:
        return self.outer_radius_in * 2.0

    @property
    def full_height_in(self) -> float:
        return (
            self.outer_head_depth_in
            + self.straight_shell_height_in
            + self.outer_head_depth_in
        )

    @property
    def outer_head_depth_in(self) -> float:
        return self.head_depth_for_offset_in(self.total_shell_thickness_in)

    @property
    def glass_height_mm(self) -> float:
        return self.glass_depth_in * MM_PER_INCH

    @property
    def straight_shell_height_mm(self) -> float:
        return self.straight_shell_height_in * MM_PER_INCH

    @property
    def electrode_centerline_height_in(self) -> float:
        return self.glass_depth_in * self.electrode_centerline_height_fraction

    @property
    def electrode_centerline_height_mm(self) -> float:
        return self.electrode_centerline_height_in * MM_PER_INCH

    @property
    def electrode_radius_in(self) -> float:
        return self.electrode_diameter_in * 0.5

    @property
    def electrode_radius_mm(self) -> float:
        return self.electrode_radius_in * MM_PER_INCH

    @property
    def electrode_length_in(self) -> float:
        return (
            self.electrode_insertion_into_inner_circle_in
            + self.electrode_extension_past_inner_circle_in
        )

    @property
    def electrode_length_mm(self) -> float:
        return self.electrode_length_in * MM_PER_INCH

    @property
    def electrode_inner_tip_radius_in(self) -> float:
        return self.inner_radius_in - self.electrode_insertion_into_inner_circle_in

    @property
    def electrode_outer_tip_radius_in(self) -> float:
        return self.inner_radius_in + self.electrode_extension_past_inner_circle_in

    @property
    def layers(self) -> tuple[MaterialLayer, ...]:
        materials = self.material_properties_by_name
        return (
            MaterialLayer(materials["glass_bath"], self.inner_radius_in),
            MaterialLayer(materials["hot_face_refractory"], self.hot_face_thickness_in),
            MaterialLayer(materials["ifb"], self.ifb_thickness_in),
            MaterialLayer(materials["duraboard"], self.duraboard_thickness_in),
            MaterialLayer(materials["steel_shell"], self.steel_thickness_in),
        )

    @property
    def material_properties_by_name(self) -> dict[str, MaterialProperties]:
        return dict(DEFAULT_VESSEL_MATERIALS_BY_NAME)

    @property
    def shell_bands(self) -> tuple[RadialBand, ...]:
        running_radius = self.inner_radius_in
        bands: list[RadialBand] = []
        for layer in self.layers[1:]:
            outer_radius = running_radius + layer.thickness_in
            bands.append(
                RadialBand(
                    name=layer.name,
                    color_hex=layer.color_hex,
                    inner_radius_in=running_radius,
                    outer_radius_in=outer_radius,
                )
            )
            running_radius = outer_radius
        return tuple(bands)

    @property
    def radial_bands(self) -> tuple[RadialBand, ...]:
        glass = self.layers[0]
        return (
            RadialBand(
                name=glass.name,
                color_hex=glass.color_hex,
                inner_radius_in=0.0,
                outer_radius_in=self.inner_radius_in,
            ),
            *self.shell_bands,
        )

    @property
    def electrode_placements(self) -> tuple[VesselElectrodePlacement, ...]:
        placements: list[VesselElectrodePlacement] = []
        for index in range(self.electrode_count):
            angle_degrees = index * (360.0 / self.electrode_count)
            placements.append(
                VesselElectrodePlacement(
                    index=index + 1,
                    angle_degrees=angle_degrees,
                    angle_radians=radians(angle_degrees),
                    inner_tip_radius_in=self.electrode_inner_tip_radius_in,
                    outer_tip_radius_in=self.electrode_outer_tip_radius_in,
                    diameter_in=self.electrode_diameter_in,
                )
            )
        return tuple(placements)

    def head_depth_for_offset_in(self, offset_in: float) -> float:
        require_nonnegative("offset_in", offset_in)
        return self.head_depth_in + offset_in

    def _validate_side_ports(self) -> None:
        for index, port in enumerate(self.side_ports):
            require_less_or_equal(
                f"side_ports[{index}].height_above_glass_surface_in",
                port.height_above_glass_surface_in + port.radius_in,
                self.plenum_height_in,
            )
            require_less_or_equal(
                f"side_ports[{index}].diameter_in",
                port.radius_in,
                port.height_above_glass_surface_in,
            )

    def _validate_lid_ports(self) -> None:
        for index, port in enumerate(self.lid_ports):
            require_less_or_equal(
                f"lid_ports[{index}].radial_distance_from_center_in",
                port.radial_distance_from_center_in + port.radius_in,
                self.outer_radius_in,
            )

    def to_manifest(self) -> dict[str, Any]:
        return build_vessel_drafter_manifest(self)


DEFAULT_VESSEL_DRAFTER_LAYOUT = VesselDrafterLayout()
