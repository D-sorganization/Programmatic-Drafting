"""Status text formatting for the vessel drafter main window."""

from __future__ import annotations

from programmatic_drafting.analysis.vessel_drafter_metrics import MaterialMetricsReport
from programmatic_drafting.models.vessel_drafter import VesselDrafterLayout


def format_status_text(
    layout: VesselDrafterLayout,
    metrics: MaterialMetricsReport,
) -> str:
    """Build the compact status summary shown after preview refresh."""
    return (
        f"Outer diameter: {layout.outer_diameter_in:.2f} in | "
        f"Full height: {layout.full_height_in:.2f} in | "
        f"Ports: {len(layout.side_ports)} side, {len(layout.lid_ports)} lid | "
        f"Refractory: {metrics.refractory_total_volume_ft3:.2f} ft^3, "
        f"{metrics.refractory_total_surface_area_ft2:.2f} ft^2, "
        f"{metrics.refractory_total_mass_lb:.1f} lb"
    )
