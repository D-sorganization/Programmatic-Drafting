"""Modal dialog helpers for adding vessel side and lid ports.

These factories wrap :class:`PortValueDialog` with the field specifications
used by the main window. They return ``None`` if the user cancels the dialog
so callers can branch cleanly without worrying about Qt's ``QDialog.exec``
return codes.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QWidget

from programmatic_drafting.gui.vessel_drafter_port_panel import (
    PortFieldSpec,
    PortValueDialog,
)
from programmatic_drafting.models.vessel_drafter import (
    VesselLidPort,
    VesselSidePort,
)

_SIDE_PORT_FIELDS: tuple[PortFieldSpec, ...] = (
    PortFieldSpec("Clock angle (deg)", 0.0, 0.0, 360.0),
    PortFieldSpec("Diameter (in)", 3.0, 0.1, 100.0),
    PortFieldSpec("Height above glass (in)", 4.0, 0.0, 250.0),
)

_LID_PORT_FIELDS: tuple[PortFieldSpec, ...] = (
    PortFieldSpec("Clock angle (deg)", 0.0, 0.0, 360.0),
    PortFieldSpec("Diameter (in)", 4.0, 0.1, 100.0),
    PortFieldSpec("Distance from center (in)", 8.0, 0.0, 500.0),
)


def prompt_add_side_port(parent: QWidget) -> VesselSidePort | None:
    """Run the add-side-port dialog and return the chosen port, or ``None``."""
    dialog = PortValueDialog("Add Side Port", _SIDE_PORT_FIELDS, parent)
    if not dialog.exec():
        return None
    angle, diameter, height = dialog.values()
    return VesselSidePort(
        clock_angle_degrees=angle,
        diameter_in=diameter,
        height_above_glass_surface_in=height,
    )


def prompt_add_lid_port(parent: QWidget) -> VesselLidPort | None:
    """Run the add-lid-port dialog and return the chosen port, or ``None``."""
    dialog = PortValueDialog("Add Lid Port", _LID_PORT_FIELDS, parent)
    if not dialog.exec():
        return None
    angle, diameter, radius = dialog.values()
    return VesselLidPort(
        clock_angle_degrees=angle,
        diameter_in=diameter,
        radial_distance_from_center_in=radius,
    )
