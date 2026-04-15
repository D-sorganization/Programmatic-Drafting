from __future__ import annotations

from PyQt6.QtCore import Qt

from programmatic_drafting.gui.vessel_drafter_rendering import (
    PREVIEW_MARGIN,
    PREVIEW_SCALE,
    _build_projected_side_port_item,
    _projected_side_port_center,
)
from programmatic_drafting.preview.vessel_drafter_preview import (
    CrossSectionPreview,
    ProjectedSidePort,
)


def _preview() -> CrossSectionPreview:
    return CrossSectionPreview(
        inner_radius_in=10.0,
        outer_radius_in=12.0,
        straight_shell_height_in=20.0,
        inner_head_depth_in=2.0,
        outer_head_depth_in=3.0,
        glass_height_in=8.0,
        plenum_height_in=12.0,
        electrode_diameter_in=2.0,
        bands=(),
        band_polygons=(),
        plenum_loop=(),
        projected_side_ports=(),
        axial_electrodes=(),
    )


def test_projected_side_port_center_maps_right_edge() -> None:
    port = ProjectedSidePort(
        clock_angle_degrees=90.0,
        centerline_height_in=7.0,
        diameter_in=2.0,
    )
    center = _projected_side_port_center(
        preview=_preview(),
        center_x=120.0,
        top_z_in=23.0,
        port=port,
        direction=1.0,
    )

    assert center.x() == 120.0 + ((12.0 - 1.0) * PREVIEW_SCALE)
    assert center.y() == PREVIEW_MARGIN + ((23.0 - 7.0) * PREVIEW_SCALE)


def test_projected_side_port_item_is_dashed_and_unfilled() -> None:
    item = _build_projected_side_port_item(
        center=_projected_side_port_center(
            preview=_preview(),
            center_x=120.0,
            top_z_in=23.0,
            port=ProjectedSidePort(0.0, 7.0, 2.0),
            direction=-1.0,
        ),
        radius_px=8.0,
    )

    assert item.pen().style() == Qt.PenStyle.DashLine
    assert item.brush().style() == Qt.BrushStyle.NoBrush
