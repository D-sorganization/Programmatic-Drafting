"""PyQt6 GUI for the vessel drafter tool."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from programmatic_drafting.exporters.step_export import export_vessel_drafter_step
from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    RadialBand,
    VesselDrafterLayout,
)
from programmatic_drafting.preview.vessel_drafter_preview import (
    build_cross_section_preview,
    build_plan_preview,
)


def _make_double_spin(value: float, minimum: float, maximum: float) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(minimum, maximum)
    spin.setDecimals(2)
    spin.setSingleStep(0.5)
    spin.setValue(value)
    return spin


def _band_pen() -> QPen:
    pen = QPen(QColor("#2B2B2B"))
    pen.setWidth(1)
    return pen


def _add_path(
    scene: QGraphicsScene,
    path: QPainterPath,
    color_hex: str,
    z_value: float = 0.0,
) -> None:
    item = QGraphicsPathItem(path)
    item.setPen(_band_pen())
    item.setBrush(QBrush(QColor(color_hex)))
    item.setZValue(z_value)
    scene.addItem(item)


class VesselDrafterWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Vessel Drafter")
        self.resize(1200, 720)

        self.inner_diameter_spin = _make_double_spin(50.0, 1.0, 500.0)
        self.glass_depth_spin = _make_double_spin(14.0, 1.0, 250.0)
        self.plenum_height_spin = _make_double_spin(14.0, 1.0, 250.0)
        self.head_depth_spin = _make_double_spin(12.5, 1.0, 250.0)
        self.hot_face_spin = _make_double_spin(6.0, 0.1, 50.0)
        self.ifb_spin = _make_double_spin(4.5, 0.1, 50.0)
        self.duraboard_spin = _make_double_spin(1.0, 0.1, 20.0)
        self.steel_spin = _make_double_spin(0.5, 0.1, 10.0)
        self.electrode_count_spin = QSpinBox()
        self.electrode_count_spin.setRange(1, 12)
        self.electrode_count_spin.setValue(3)
        self.electrode_diameter_spin = _make_double_spin(2.0, 0.1, 20.0)
        self.electrode_insertion_spin = _make_double_spin(14.0, 0.1, 100.0)
        self.electrode_extension_spin = _make_double_spin(36.0, 0.1, 150.0)

        self.cross_section_scene = QGraphicsScene(self)
        self.cross_section_view = QGraphicsView(self.cross_section_scene)
        self.plan_scene = QGraphicsScene(self)
        self.plan_view = QGraphicsView(self.plan_scene)
        self.status_label = QLabel()

        self._build_ui()
        self._connect_signals()
        self.write_layout(DEFAULT_VESSEL_DRAFTER_LAYOUT)
        self.update_preview()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        form_layout = QFormLayout()
        form_layout.addRow("Inner diameter (in)", self.inner_diameter_spin)
        form_layout.addRow("Glass depth (in)", self.glass_depth_spin)
        form_layout.addRow("Plenum height (in)", self.plenum_height_spin)
        form_layout.addRow("Head depth (in)", self.head_depth_spin)
        form_layout.addRow("Hot face (in)", self.hot_face_spin)
        form_layout.addRow("IFB (in)", self.ifb_spin)
        form_layout.addRow("Duraboard (in)", self.duraboard_spin)
        form_layout.addRow("Steel (in)", self.steel_spin)
        form_layout.addRow("Electrode count", self.electrode_count_spin)
        form_layout.addRow("Electrode diameter (in)", self.electrode_diameter_spin)
        form_layout.addRow("Electrode insertion (in)", self.electrode_insertion_spin)
        form_layout.addRow("Electrode extension (in)", self.electrode_extension_spin)

        update_button = QPushButton("Refresh Preview")
        update_button.clicked.connect(self.update_preview)
        export_button = QPushButton("Export STEP")
        export_button.clicked.connect(self.export_step_dialog)

        controls_layout = QVBoxLayout()
        controls_layout.addLayout(form_layout)
        controls_layout.addWidget(update_button)
        controls_layout.addWidget(export_button)
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch(1)

        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Cross-Section Preview"))
        preview_layout.addWidget(self.cross_section_view, 1)
        preview_layout.addWidget(QLabel("Top View Preview"))
        preview_layout.addWidget(self.plan_view, 1)

        main_layout = QHBoxLayout(root)
        main_layout.addLayout(controls_layout, 0)
        main_layout.addLayout(preview_layout, 1)

    def _connect_signals(self) -> None:
        widgets = (
            self.inner_diameter_spin,
            self.glass_depth_spin,
            self.plenum_height_spin,
            self.head_depth_spin,
            self.hot_face_spin,
            self.ifb_spin,
            self.duraboard_spin,
            self.steel_spin,
            self.electrode_count_spin,
            self.electrode_diameter_spin,
            self.electrode_insertion_spin,
            self.electrode_extension_spin,
        )
        for widget in widgets:
            widget.valueChanged.connect(self.update_preview)

    def write_layout(self, layout: VesselDrafterLayout) -> None:
        self.inner_diameter_spin.setValue(layout.inner_diameter_in)
        self.glass_depth_spin.setValue(layout.glass_depth_in)
        self.plenum_height_spin.setValue(layout.plenum_height_in)
        self.head_depth_spin.setValue(layout.head_depth_in)
        self.hot_face_spin.setValue(layout.hot_face_thickness_in)
        self.ifb_spin.setValue(layout.ifb_thickness_in)
        self.duraboard_spin.setValue(layout.duraboard_thickness_in)
        self.steel_spin.setValue(layout.steel_thickness_in)
        self.electrode_count_spin.setValue(layout.electrode_count)
        self.electrode_diameter_spin.setValue(layout.electrode_diameter_in)
        self.electrode_insertion_spin.setValue(
            layout.electrode_insertion_into_inner_circle_in
        )
        self.electrode_extension_spin.setValue(
            layout.electrode_extension_past_inner_circle_in
        )

    def read_layout(self) -> VesselDrafterLayout:
        return VesselDrafterLayout(
            inner_diameter_in=self.inner_diameter_spin.value(),
            glass_depth_in=self.glass_depth_spin.value(),
            plenum_height_in=self.plenum_height_spin.value(),
            head_depth_in=self.head_depth_spin.value(),
            hot_face_thickness_in=self.hot_face_spin.value(),
            ifb_thickness_in=self.ifb_spin.value(),
            duraboard_thickness_in=self.duraboard_spin.value(),
            steel_thickness_in=self.steel_spin.value(),
            electrode_count=self.electrode_count_spin.value(),
            electrode_diameter_in=self.electrode_diameter_spin.value(),
            electrode_insertion_into_inner_circle_in=self.electrode_insertion_spin.value(),
            electrode_extension_past_inner_circle_in=self.electrode_extension_spin.value(),
        )

    def update_preview(self) -> None:
        try:
            layout = self.read_layout()
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return

        self._render_cross_section(layout)
        self._render_plan(layout)
        self.status_label.setText(
            f"Outer diameter: {layout.outer_diameter_in:.2f} in | "
            f"Full height: {layout.full_height_in:.2f} in"
        )

    def export_step_dialog(self) -> None:
        try:
            layout = self.read_layout()
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return

        target, _ = QFileDialog.getSaveFileName(
            self,
            "Export vessel STEP",
            str(
                Path.cwd()
                / "generated/vessel_drafter_default/vessel_drafter_default.step"
            ),
            "STEP Files (*.step *.stp)",
        )
        if not target:
            return

        output_path = Path(target)
        manifest_path = output_path.with_suffix(".json")
        export_vessel_drafter_step(
            output_path=output_path,
            manifest_path=manifest_path,
            layout=layout,
        )
        self.status_label.setText(f"Exported {output_path}")

    def _render_cross_section(self, layout: VesselDrafterLayout) -> None:
        preview = build_cross_section_preview(layout)
        scene = self.cross_section_scene
        scene.clear()

        scale = 8.0
        margin = 24.0
        scene_height = (
            preview.outer_head_depth_in
            + preview.straight_shell_height_in
            + preview.outer_head_depth_in
        ) * scale
        scene_width = (preview.outer_radius_in * 2.0) * scale
        center_x = margin + (scene_width * 0.5)
        base_y = margin + (preview.outer_head_depth_in * scale)
        scene.setSceneRect(
            0.0, 0.0, scene_width + (margin * 2.0), scene_height + (margin * 2.0)
        )

        for band in layout.shell_bands:
            self._render_sidewall_band(scene, band, layout, center_x, base_y, scale)
            self._render_head_band(scene, band, layout, center_x, base_y, scale, True)
            self._render_head_band(scene, band, layout, center_x, base_y, scale, False)

        glass_path = QPainterPath()
        glass_radius_px = preview.inner_radius_in * scale
        glass_height_px = preview.glass_height_in * scale
        glass_path.addRect(
            center_x - glass_radius_px,
            base_y
            + ((preview.straight_shell_height_in - preview.glass_height_in) * scale),
            glass_radius_px * 2.0,
            glass_height_px,
        )
        _add_path(scene, glass_path, layout.layers[0].color_hex, 5.0)

        plenum_path = QPainterPath()
        plenum_path.addRect(
            center_x - glass_radius_px,
            base_y,
            glass_radius_px * 2.0,
            preview.plenum_height_in * scale,
        )
        plenum_item = QGraphicsPathItem(plenum_path)
        plenum_pen = QPen(QColor("#6AAED6"))
        plenum_pen.setStyle(Qt.PenStyle.DashLine)
        plenum_item.setPen(plenum_pen)
        plenum_item.setBrush(QBrush(QColor("#DCEEFF")))
        plenum_item.setOpacity(0.4)
        scene.addItem(plenum_item)

    def _render_sidewall_band(
        self,
        scene: QGraphicsScene,
        band: RadialBand,
        layout: VesselDrafterLayout,
        center_x: float,
        base_y: float,
        scale: float,
    ) -> None:
        outer_radius_px = band.outer_radius_in * scale
        inner_radius_px = band.inner_radius_in * scale
        wall_height_px = layout.straight_shell_height_in * scale

        path = QPainterPath()
        path.addRect(
            center_x - outer_radius_px,
            base_y,
            outer_radius_px - inner_radius_px,
            wall_height_px,
        )
        path.addRect(
            center_x + inner_radius_px,
            base_y,
            outer_radius_px - inner_radius_px,
            wall_height_px,
        )
        _add_path(scene, path, band.color_hex, 1.0)

    def _render_head_band(
        self,
        scene: QGraphicsScene,
        band: RadialBand,
        layout: VesselDrafterLayout,
        center_x: float,
        base_y: float,
        scale: float,
        top: bool,
    ) -> None:
        outer_radius_px = band.outer_radius_in * scale
        inner_radius_px = band.inner_radius_in * scale
        outer_depth_px = layout.head_depth_for_radius_in(band.outer_radius_in) * scale
        inner_depth_px = layout.head_depth_for_radius_in(band.inner_radius_in) * scale

        springline_y = (
            base_y if not top else base_y + (layout.straight_shell_height_in * scale)
        )
        outer_rect_y = springline_y - (outer_depth_px * 2.0) if top else springline_y
        inner_rect_y = springline_y - (inner_depth_px * 2.0) if top else springline_y

        outer_path = QPainterPath()
        outer_path.addEllipse(
            center_x - outer_radius_px,
            outer_rect_y,
            outer_radius_px * 2.0,
            outer_depth_px * 2.0,
        )
        inner_path = QPainterPath()
        inner_path.addEllipse(
            center_x - inner_radius_px,
            inner_rect_y,
            inner_radius_px * 2.0,
            inner_depth_px * 2.0,
        )
        band_path = outer_path.subtracted(inner_path)
        clip_path = QPainterPath()
        if top:
            clip_path.addRect(
                center_x - (outer_radius_px * 1.2),
                springline_y - (outer_depth_px * 1.2),
                outer_radius_px * 2.4,
                outer_depth_px * 1.2,
            )
        else:
            clip_path.addRect(
                center_x - (outer_radius_px * 1.2),
                springline_y,
                outer_radius_px * 2.4,
                outer_depth_px * 1.2,
            )
        _add_path(scene, band_path.intersected(clip_path), band.color_hex, 2.0)

    def _render_plan(self, layout: VesselDrafterLayout) -> None:
        preview = build_plan_preview(layout)
        scene = self.plan_scene
        scene.clear()

        scale = 8.0
        margin = 24.0
        diameter_px = preview.outer_radius_in * 2.0 * scale
        center_x = margin + (diameter_px * 0.5)
        center_y = center_x
        scene.setSceneRect(
            0.0, 0.0, diameter_px + (margin * 2.0), diameter_px + (margin * 2.0)
        )

        for band in reversed(preview.bands):
            radius_px = band.outer_radius_in * scale
            ellipse = scene.addEllipse(
                center_x - radius_px,
                center_y - radius_px,
                radius_px * 2.0,
                radius_px * 2.0,
                _band_pen(),
                QBrush(QColor(band.color_hex)),
            )
            ellipse.setZValue(1.0)

        electrode_pen = QPen(QColor("#2B2B2B"))
        electrode_pen.setWidth(3)
        for placement in preview.electrodes:
            inner_radius_px = placement.inner_tip_radius_in * scale
            outer_radius_px = placement.outer_tip_radius_in * scale
            cos_theta = __import__("math").cos(placement.angle_radians)
            sin_theta = __import__("math").sin(placement.angle_radians)
            scene.addLine(
                center_x + (inner_radius_px * cos_theta),
                center_y - (inner_radius_px * sin_theta),
                center_x + (outer_radius_px * cos_theta),
                center_y - (outer_radius_px * sin_theta),
                electrode_pen,
            )


def launch() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = VesselDrafterWindow()
    window.show()
    return app.exec()
