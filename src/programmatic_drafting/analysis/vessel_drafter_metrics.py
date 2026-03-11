"""Volume and mass metrics for the vessel drafter model."""

from __future__ import annotations

from dataclasses import dataclass

from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    MM_PER_INCH,
    VesselDrafterLayout,
)
from programmatic_drafting.projects.vessel_drafter_layout import (
    VesselComponent,
    build_vessel_drafter_components,
)

CUBIC_INCHES_PER_CUBIC_FOOT = 1728.0


@dataclass(frozen=True)
class ComponentMaterialMetric:
    label: str
    display_name: str
    category: str
    volume_in3: float
    density_lb_per_ft3: float
    mass_lb: float
    thermal_conductivity_w_per_mk: float
    thermal_expansion_um_per_m_c: float


@dataclass(frozen=True)
class MaterialMetricsReport:
    component_metrics: tuple[ComponentMaterialMetric, ...]
    refractory_total_volume_in3: float
    refractory_total_mass_lb: float


def build_material_metrics_report(
    layout: VesselDrafterLayout = DEFAULT_VESSEL_DRAFTER_LAYOUT,
) -> MaterialMetricsReport:
    metrics = tuple(
        _component_metric(component)
        for component in build_vessel_drafter_components(layout)
        if component.category != "electrode"
    )
    refractory_metrics = tuple(
        item for item in metrics if item.category == "refractory"
    )
    return MaterialMetricsReport(
        component_metrics=metrics,
        refractory_total_volume_in3=sum(item.volume_in3 for item in refractory_metrics),
        refractory_total_mass_lb=sum(item.mass_lb for item in refractory_metrics),
    )


def _component_metric(component: VesselComponent) -> ComponentMaterialMetric:
    volume_in3 = _mm3_to_in3(component.shape.volume)
    return ComponentMaterialMetric(
        label=component.label,
        display_name=component.display_name,
        category=component.category,
        volume_in3=volume_in3,
        density_lb_per_ft3=component.density_lb_per_ft3,
        mass_lb=(volume_in3 / CUBIC_INCHES_PER_CUBIC_FOOT)
        * component.density_lb_per_ft3,
        thermal_conductivity_w_per_mk=component.thermal_conductivity_w_per_mk,
        thermal_expansion_um_per_m_c=component.thermal_expansion_um_per_m_c,
    )


def _mm3_to_in3(volume_mm3: float) -> float:
    return volume_mm3 / (MM_PER_INCH**3)
