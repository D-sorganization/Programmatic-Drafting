"""Validated defaults and geometry helpers for the vessel drafter tool."""

from __future__ import annotations

from dataclasses import dataclass
from math import radians
from typing import Any

from programmatic_drafting.contracts import (
    require_fraction,
    require_integer_at_least,
    require_less_or_equal,
    require_positive,
)

MM_PER_INCH = 25.4


@dataclass(frozen=True)
class MaterialLayer:
    name: str
    thickness_in: float
    color_hex: str


@dataclass(frozen=True)
class RadialBand:
    name: str
    color_hex: str
    inner_radius_in: float
    outer_radius_in: float

    @property
    def label(self) -> str:
        return self.name


@dataclass(frozen=True)
class VesselElectrodePlacement:
    index: int
    angle_degrees: float
    angle_radians: float
    inner_tip_radius_in: float
    outer_tip_radius_in: float


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

    @property
    def inner_radius_in(self) -> float:
        return self.inner_diameter_in * 0.5

    @property
    def straight_shell_height_in(self) -> float:
        return self.glass_depth_in + self.plenum_height_in

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
        return self.head_depth_for_radius_in(self.outer_radius_in)

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
        return (
            MaterialLayer("glass_bath", self.inner_radius_in, "#F28C28"),
            MaterialLayer(
                "hot_face_refractory",
                self.hot_face_thickness_in,
                "#D95F02",
            ),
            MaterialLayer("ifb", self.ifb_thickness_in, "#C7A46A"),
            MaterialLayer("duraboard", self.duraboard_thickness_in, "#F5F5F0"),
            MaterialLayer("steel_shell", self.steel_thickness_in, "#8A8F98"),
        )

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
                )
            )
        return tuple(placements)

    def head_depth_for_radius_in(self, radius_in: float) -> float:
        require_positive("radius_in", radius_in)
        return self.head_depth_in * (radius_in / self.inner_radius_in)

    def to_manifest(self) -> dict[str, Any]:
        return {
            "project": "vessel_drafter_default",
            "units": {"source": "inches", "cad": "millimeters"},
            "vessel": {
                "inner_diameter_in": self.inner_diameter_in,
                "glass_depth_in": self.glass_depth_in,
                "plenum_height_in": self.plenum_height_in,
                "head_depth_in": self.head_depth_in,
                "outer_diameter_in": self.outer_diameter_in,
                "full_height_in": self.full_height_in,
            },
            "materials": {
                layer.name: {
                    "thickness_in": layer.thickness_in,
                    "color_hex": layer.color_hex,
                }
                for layer in self.layers[1:]
            },
            "glass_bath": {
                "color_hex": self.layers[0].color_hex,
                "height_in": self.glass_depth_in,
            },
            "electrodes": {
                "count": self.electrode_count,
                "diameter_in": self.electrode_diameter_in,
                "insertion_into_inner_circle_in": (
                    self.electrode_insertion_into_inner_circle_in
                ),
                "extension_past_inner_circle_in": (
                    self.electrode_extension_past_inner_circle_in
                ),
                "modeled_length_in": self.electrode_length_in,
                "centerline_height_in": self.electrode_centerline_height_in,
            },
            "drafting_assumptions": {
                "axis_convention": "Z up",
                "plenum_only_internal_void": True,
                "dished_heads": "Aspect-ratio-preserving spherical-cap approximation",
            },
        }


DEFAULT_VESSEL_DRAFTER_LAYOUT = VesselDrafterLayout()
