"""Preview data builders for the vessel drafter GUI."""

from __future__ import annotations

from dataclasses import dataclass

from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    RadialBand,
    VesselDrafterLayout,
    VesselElectrodePlacement,
)


@dataclass(frozen=True)
class CrossSectionPreview:
    inner_radius_in: float
    outer_radius_in: float
    straight_shell_height_in: float
    inner_head_depth_in: float
    outer_head_depth_in: float
    glass_height_in: float
    plenum_height_in: float
    bands: tuple[RadialBand, ...]


@dataclass(frozen=True)
class PlanPreview:
    outer_radius_in: float
    bands: tuple[RadialBand, ...]
    electrodes: tuple[VesselElectrodePlacement, ...]


def build_cross_section_preview(
    layout: VesselDrafterLayout = DEFAULT_VESSEL_DRAFTER_LAYOUT,
) -> CrossSectionPreview:
    return CrossSectionPreview(
        inner_radius_in=layout.inner_radius_in,
        outer_radius_in=layout.outer_radius_in,
        straight_shell_height_in=layout.straight_shell_height_in,
        inner_head_depth_in=layout.head_depth_in,
        outer_head_depth_in=layout.outer_head_depth_in,
        glass_height_in=layout.glass_depth_in,
        plenum_height_in=layout.plenum_height_in,
        bands=layout.radial_bands,
    )


def build_plan_preview(
    layout: VesselDrafterLayout = DEFAULT_VESSEL_DRAFTER_LAYOUT,
) -> PlanPreview:
    return PlanPreview(
        outer_radius_in=layout.outer_radius_in,
        bands=layout.radial_bands,
        electrodes=layout.electrode_placements,
    )
