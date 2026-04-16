from __future__ import annotations

from math import pi

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QGraphicsScene

from programmatic_drafting.gui.vessel_drafter_rendering import (
    PREVIEW_MARGIN,
    PREVIEW_SCALE,
    _build_projected_side_port_item,
    _projected_side_port_center,
    _render_plan_bands,
    _render_plan_electrodes,
    _render_plan_ports,
)
from programmatic_drafting.models.vessel_drafter_types import (
    RadialBand,
    VesselElectrodePlacement,
)
from programmatic_drafting.preview.vessel_drafter_preview import (
    CrossSectionPreview,
    PlanCircularFeature,
    PlanPreview,
    PlanRadialFeature,
    ProjectedSidePort,
)

_app = QApplication.instance() or QApplication([])


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


def _plan_preview(
    bands: tuple[RadialBand, ...] = (),
    electrodes: tuple[VesselElectrodePlacement, ...] = (),
    side_ports: tuple[PlanRadialFeature, ...] = (),
    lid_ports: tuple[PlanCircularFeature, ...] = (),
) -> PlanPreview:
    return PlanPreview(
        outer_radius_in=12.0,
        bands=bands,
        electrodes=electrodes,
        side_ports=side_ports,
        lid_ports=lid_ports,
    )


def test_render_plan_bands_adds_one_ellipse_per_band() -> None:
    bands = (
        RadialBand("glass_bath", "#AABBCC", 0.0, 10.0),
        RadialBand("hot_face", "#112233", 10.0, 12.0),
    )
    scene = QGraphicsScene()
    _render_plan_bands(scene, _plan_preview(bands=bands), 120.0, 120.0)
    assert len(scene.items()) == 2


def test_render_plan_ports_adds_items_for_lid_and_side_ports() -> None:
    lid = PlanCircularFeature("lid_port_1", "#FF0000", 5.0, 0.0, 2.0)
    side = PlanRadialFeature("side_port_1", "#00FF00", 45.0, pi / 4, 8.0, 12.0, 1.5)
    scene = QGraphicsScene()
    _render_plan_ports(
        scene,
        _plan_preview(lid_ports=(lid,), side_ports=(side,)),
        120.0,
        120.0,
    )
    assert len(scene.items()) == 2


def test_render_plan_electrodes_adds_one_item_per_electrode() -> None:
    electrode = VesselElectrodePlacement(
        index=1,
        angle_degrees=0.0,
        angle_radians=0.0,
        inner_tip_radius_in=2.0,
        outer_tip_radius_in=10.0,
        diameter_in=2.0,
    )
    scene = QGraphicsScene()
    _render_plan_electrodes(scene, _plan_preview(electrodes=(electrode,)), 120.0, 120.0)
    assert len(scene.items()) == 1
