"""Layout read/write helpers for the vessel drafter main window."""

from __future__ import annotations

from typing import Any

from programmatic_drafting.models.vessel_drafter import (
    VesselDrafterLayout,
    VesselLidPort,
    VesselSidePort,
)

PortRow = tuple[float, float, float]


def side_port_rows(ports: tuple[VesselSidePort, ...]) -> tuple[PortRow, ...]:
    """Convert side ports into editable table rows."""
    return tuple(
        (
            port.normalized_clock_angle_degrees,
            port.diameter_in,
            port.height_above_glass_surface_in,
        )
        for port in ports
    )


def lid_port_rows(ports: tuple[VesselLidPort, ...]) -> tuple[PortRow, ...]:
    """Convert lid ports into editable table rows."""
    return tuple(
        (
            port.normalized_clock_angle_degrees,
            port.diameter_in,
            port.radial_distance_from_center_in,
        )
        for port in ports
    )


def side_ports_from_rows(rows: tuple[PortRow, ...]) -> tuple[VesselSidePort, ...]:
    """Convert side-port table rows into model objects."""
    return tuple(
        VesselSidePort(
            clock_angle_degrees=angle,
            diameter_in=diameter,
            height_above_glass_surface_in=height,
        )
        for angle, diameter, height in rows
    )


def lid_ports_from_rows(rows: tuple[PortRow, ...]) -> tuple[VesselLidPort, ...]:
    """Convert lid-port table rows into model objects."""
    return tuple(
        VesselLidPort(
            clock_angle_degrees=angle,
            diameter_in=diameter,
            radial_distance_from_center_in=radius,
        )
        for angle, diameter, radius in rows
    )


def write_layout_to_controls(window: Any, layout: VesselDrafterLayout) -> None:
    """Write a layout into window controls without triggering preview refreshes."""
    window._suppress_preview_updates = True
    try:
        _write_scalar_controls(window, layout)
        window.side_port_panel.set_rows(side_port_rows(layout.side_ports))
        window.lid_port_panel.set_rows(lid_port_rows(layout.lid_ports))
    finally:
        window._suppress_preview_updates = False


def read_layout_from_controls(window: Any) -> VesselDrafterLayout:
    """Read the current window controls into a validated layout."""
    return VesselDrafterLayout(
        inner_diameter_in=window.inner_diameter_spin.value(),
        glass_depth_in=window.glass_depth_spin.value(),
        plenum_height_in=window.plenum_height_spin.value(),
        head_depth_in=window.head_depth_spin.value(),
        hot_face_thickness_in=window.hot_face_spin.value(),
        ifb_thickness_in=window.ifb_spin.value(),
        duraboard_thickness_in=window.duraboard_spin.value(),
        steel_thickness_in=window.steel_spin.value(),
        electrode_count=window.electrode_count_spin.value(),
        electrode_diameter_in=window.electrode_diameter_spin.value(),
        electrode_insertion_into_inner_circle_in=window.electrode_insertion_spin.value(),
        electrode_extension_past_inner_circle_in=window.electrode_extension_spin.value(),
        side_ports=side_ports_from_rows(window.side_port_panel.rows()),
        lid_ports=lid_ports_from_rows(window.lid_port_panel.rows()),
    )


def add_side_port_to_controls(window: Any, port: VesselSidePort) -> None:
    """Append a side port row to the window's editable table."""
    window.side_port_panel.append_row(side_port_rows((port,))[0])


def add_lid_port_to_controls(window: Any, port: VesselLidPort) -> None:
    """Append a lid port row to the window's editable table."""
    window.lid_port_panel.append_row(lid_port_rows((port,))[0])


def _write_scalar_controls(window: Any, layout: VesselDrafterLayout) -> None:
    window.inner_diameter_spin.setValue(layout.inner_diameter_in)
    window.glass_depth_spin.setValue(layout.glass_depth_in)
    window.plenum_height_spin.setValue(layout.plenum_height_in)
    window.head_depth_spin.setValue(layout.head_depth_in)
    window.hot_face_spin.setValue(layout.hot_face_thickness_in)
    window.ifb_spin.setValue(layout.ifb_thickness_in)
    window.duraboard_spin.setValue(layout.duraboard_thickness_in)
    window.steel_spin.setValue(layout.steel_thickness_in)
    window.electrode_count_spin.setValue(layout.electrode_count)
    window.electrode_diameter_spin.setValue(layout.electrode_diameter_in)
    window.electrode_insertion_spin.setValue(
        layout.electrode_insertion_into_inner_circle_in
    )
    window.electrode_extension_spin.setValue(
        layout.electrode_extension_past_inner_circle_in
    )
