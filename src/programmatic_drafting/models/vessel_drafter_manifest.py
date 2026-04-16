"""Manifest-builder helpers for :class:`VesselDrafterLayout`.

These functions convert a validated layout (and its constituent types)
into plain-dictionary manifest entries suitable for serialization. The
aggregate ``to_manifest`` call on ``VesselDrafterLayout`` composes these
builders into a single manifest document.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from programmatic_drafting.models.vessel_drafter_types import (
    MaterialLayer,
    VesselLidPort,
    VesselSidePort,
)

if TYPE_CHECKING:
    from programmatic_drafting.models.vessel_drafter import VesselDrafterLayout


def build_vessel_drafter_manifest(
    layout: VesselDrafterLayout,
) -> dict[str, Any]:
    """Build the full vessel drafter manifest."""
    return {
        "project": "vessel_drafter_default",
        "units": {"source": "inches", "cad": "millimeters"},
        "vessel": _build_vessel_manifest(layout),
        "materials": _build_shell_materials_manifest(layout.layers[1:]),
        "glass_bath": _build_glass_bath_manifest(
            layout.layers[0],
            layout.glass_depth_in,
        ),
        "electrodes": _build_electrodes_manifest(layout),
        "ports": _build_ports_manifest(layout),
        "drafting_assumptions": _build_drafting_assumptions_manifest(),
    }


def _build_vessel_manifest(layout: VesselDrafterLayout) -> dict[str, Any]:
    """Build the vessel geometry section for a manifest.

    Preconditions:
        layout must be a validated VesselDrafterLayout.
    """
    return {
        "inner_diameter_in": layout.inner_diameter_in,
        "glass_depth_in": layout.glass_depth_in,
        "plenum_height_in": layout.plenum_height_in,
        "head_depth_in": layout.head_depth_in,
        "outer_diameter_in": layout.outer_diameter_in,
        "full_height_in": layout.full_height_in,
        "outer_head_depth_in": layout.outer_head_depth_in,
    }


def _build_shell_materials_manifest(
    layers: tuple[MaterialLayer, ...],
) -> dict[str, Any]:
    """Build the material section for the shell layers."""
    return {layer.name: _build_material_manifest(layer) for layer in layers}


def _build_material_manifest(layer: MaterialLayer) -> dict[str, Any]:
    """Build one shell material manifest entry.

    Preconditions:
        layer must be a validated MaterialLayer.
    """
    return {
        "thickness_in": layer.thickness_in,
        "display_name": layer.display_name,
        "color_hex": layer.color_hex,
        "density_lb_per_ft3": layer.density_lb_per_ft3,
        "thermal_conductivity_w_per_mk": layer.thermal_conductivity_w_per_mk,
        "thermal_expansion_um_per_m_c": layer.thermal_expansion_um_per_m_c,
    }


def _build_glass_bath_manifest(
    layer: MaterialLayer,
    height_in: float,
) -> dict[str, Any]:
    """Build the glass bath manifest entry.

    Preconditions:
        layer must be the validated glass bath layer for the layout.
        height_in must match the layout's glass depth.
    """
    return {
        "display_name": layer.display_name,
        "color_hex": layer.color_hex,
        "height_in": height_in,
        "density_lb_per_ft3": layer.density_lb_per_ft3,
        "thermal_conductivity_w_per_mk": layer.thermal_conductivity_w_per_mk,
        "thermal_expansion_um_per_m_c": layer.thermal_expansion_um_per_m_c,
    }


def _build_electrodes_manifest(layout: VesselDrafterLayout) -> dict[str, Any]:
    """Build the electrode manifest section."""
    return {
        "count": layout.electrode_count,
        "diameter_in": layout.electrode_diameter_in,
        "insertion_into_inner_circle_in": (
            layout.electrode_insertion_into_inner_circle_in
        ),
        "extension_past_inner_circle_in": (
            layout.electrode_extension_past_inner_circle_in
        ),
        "modeled_length_in": layout.electrode_length_in,
        "centerline_height_in": layout.electrode_centerline_height_in,
    }


def _build_ports_manifest(layout: VesselDrafterLayout) -> dict[str, Any]:
    """Build the side and lid port manifest sections."""
    return {
        "side": [_build_side_port_manifest(layout, port) for port in layout.side_ports],
        "lid": [_build_lid_port_manifest(port) for port in layout.lid_ports],
    }


def _build_side_port_manifest(
    layout: VesselDrafterLayout,
    port: VesselSidePort,
) -> dict[str, Any]:
    """Build one side-port manifest entry.

    Preconditions:
        layout must be a validated VesselDrafterLayout.
        port must be a validated VesselSidePort associated with the layout.
    """
    return {
        "clock_angle_degrees": port.normalized_clock_angle_degrees,
        "diameter_in": port.diameter_in,
        "height_above_glass_surface_in": port.height_above_glass_surface_in,
        "centerline_height_in": port.centerline_height_in(layout),
    }


def _build_lid_port_manifest(port: VesselLidPort) -> dict[str, Any]:
    """Build one lid-port manifest entry.

    Preconditions:
        port must be a validated VesselLidPort.
    """
    return {
        "clock_angle_degrees": port.normalized_clock_angle_degrees,
        "diameter_in": port.diameter_in,
        "radial_distance_from_center_in": port.radial_distance_from_center_in,
    }


def _build_drafting_assumptions_manifest() -> dict[str, Any]:
    """Build the fixed drafting assumptions section."""
    return {
        "axis_convention": "Z up",
        "plenum_only_internal_void": True,
        "dished_heads": (
            "Offset elliptical head profiles with constant-thickness shell layers"
        ),
    }
