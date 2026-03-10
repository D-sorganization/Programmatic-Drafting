"""PyQt6 GUI for the vessel drafter tool."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGraphicsScene,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from programmatic_drafting.exporters.step_export import export_vessel_drafter_step
from programmatic_drafting.gui.vessel_drafter_port_panel import (
    PortFieldSpec,
    PortTableSection,
    PortValueDialog,
    make_double_spin,
)
from programmatic_drafting.gui.vessel_drafter_rendering import (
    render_cross_section,
    render_plan,
)
from programmatic_drafting.gui.zoomable_graphics_view import ZoomableGraphicsView
from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    VesselDrafterLayout,
    VesselLidPort,
    VesselSidePort,
)
from programmatic_drafting.preview.vessel_drafter_preview import (
    build_cross_section_preview,
    build_plan_preview,
)


class VesselDrafterWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Vessel Drafter")
        self.resize(1400, 880)
        self._suppress_preview_updates = False

        self.inner_diameter_spin = make_double_spin(50.0, 1.0, 500.0)
        self.glass_depth_spin = make_double_spin(14.0, 1.0, 250.0)
        self.plenum_height_spin = make_double_spin(14.0, 1.0, 250.0)
        self.head_depth_spin = make_double_spin(12.5, 1.0, 250.0)
        self.hot_face_spin = make_double_spin(6.0, 0.1, 50.0)
        self.ifb_spin = make_double_spin(4.5, 0.1, 50.0)
        self.duraboard_spin = make_double_spin(1.0, 0.1, 20.0)
        self.steel_spin = make_double_spin(0.5, 0.1, 10.0)
        self.electrode_count_spin = QSpinBox()
        self.electrode_count_spin.setRange(1, 12)
        self.electrode_count_spin.setValue(3)
        self.electrode_diameter_spin = make_double_spin(2.0, 0.1, 20.0)
        self.electrode_insertion_spin = make_double_spin(14.0, 0.1, 100.0)
        self.electrode_extension_spin = make_double_spin(36.0, 0.1, 150.0)

        self.side_port_panel = PortTableSection(
            "Side Ports",
            ("Clock Angle", "Diameter", "Height Above Glass"),
        )
        self.lid_port_panel = PortTableSection(
            "Lid Ports",
            ("Clock Angle", "Diameter", "Distance From Center"),
        )

        self.cross_section_scene = QGraphicsScene(self)
        self.cross_section_view = ZoomableGraphicsView(self)
        self.cross_section_view.setScene(self.cross_section_scene)
        self.plan_scene = QGraphicsScene(self)
        self.plan_view = ZoomableGraphicsView(self)
        self.plan_view.setScene(self.plan_scene)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)

        self._build_ui()
        self._connect_signals()
        self.write_layout(DEFAULT_VESSEL_DRAFTER_LAYOUT)
        self.update_preview()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        controls_form = QFormLayout()
        controls_form.addRow("Inner diameter (in)", self.inner_diameter_spin)
        controls_form.addRow("Glass depth (in)", self.glass_depth_spin)
        controls_form.addRow("Plenum height (in)", self.plenum_height_spin)
        controls_form.addRow("Head depth (in)", self.head_depth_spin)
        controls_form.addRow("Hot face (in)", self.hot_face_spin)
        controls_form.addRow("IFB (in)", self.ifb_spin)
        controls_form.addRow("Duraboard (in)", self.duraboard_spin)
        controls_form.addRow("Steel (in)", self.steel_spin)
        controls_form.addRow("Electrode count", self.electrode_count_spin)
        controls_form.addRow("Electrode diameter (in)", self.electrode_diameter_spin)
        controls_form.addRow("Electrode insertion (in)", self.electrode_insertion_spin)
        controls_form.addRow("Electrode extension (in)", self.electrode_extension_spin)

        refresh_button = QPushButton("Refresh Preview")
        refresh_button.clicked.connect(self.update_preview)
        export_button = QPushButton("Export STEP")
        export_button.clicked.connect(self.export_step_dialog)

        controls_root = QWidget()
        controls_layout = QVBoxLayout(controls_root)
        controls_layout.addLayout(controls_form)
        controls_layout.addWidget(self.side_port_panel)
        controls_layout.addWidget(self.lid_port_panel)
        controls_layout.addWidget(refresh_button)
        controls_layout.addWidget(export_button)
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch(1)

        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        controls_scroll.setWidget(controls_root)
        controls_scroll.setMinimumWidth(340)

        preview_layout = QVBoxLayout()
        preview_layout.addWidget(
            self._build_preview_panel("Cross-Section Preview", self.cross_section_view),
            1,
        )
        preview_layout.addWidget(
            self._build_preview_panel("Top View Preview", self.plan_view),
            1,
        )

        main_layout = QHBoxLayout(root)
        main_layout.addWidget(controls_scroll, 0)
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

        self.side_port_panel.add_button.clicked.connect(self._prompt_add_side_port)
        self.lid_port_panel.add_button.clicked.connect(self._prompt_add_lid_port)
        self.side_port_panel.remove_button.clicked.connect(
            self._remove_selected_side_ports
        )
        self.lid_port_panel.remove_button.clicked.connect(
            self._remove_selected_lid_ports
        )
        self.side_port_panel.table.itemChanged.connect(self.update_preview)
        self.lid_port_panel.table.itemChanged.connect(self.update_preview)

    def write_layout(self, layout: VesselDrafterLayout) -> None:
        self._suppress_preview_updates = True
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
        self.side_port_panel.set_rows(
            tuple(
                (
                    port.normalized_clock_angle_degrees,
                    port.diameter_in,
                    port.height_above_glass_surface_in,
                )
                for port in layout.side_ports
            )
        )
        self.lid_port_panel.set_rows(
            tuple(
                (
                    port.normalized_clock_angle_degrees,
                    port.diameter_in,
                    port.radial_distance_from_center_in,
                )
                for port in layout.lid_ports
            )
        )
        self._suppress_preview_updates = False

    def add_side_port(self, port: VesselSidePort) -> None:
        self.side_port_panel.append_row(
            (
                port.normalized_clock_angle_degrees,
                port.diameter_in,
                port.height_above_glass_surface_in,
            )
        )
        self.update_preview()

    def add_lid_port(self, port: VesselLidPort) -> None:
        self.lid_port_panel.append_row(
            (
                port.normalized_clock_angle_degrees,
                port.diameter_in,
                port.radial_distance_from_center_in,
            )
        )
        self.update_preview()

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
            side_ports=tuple(
                VesselSidePort(
                    clock_angle_degrees=angle,
                    diameter_in=diameter,
                    height_above_glass_surface_in=height,
                )
                for angle, diameter, height in self.side_port_panel.rows()
            ),
            lid_ports=tuple(
                VesselLidPort(
                    clock_angle_degrees=angle,
                    diameter_in=diameter,
                    radial_distance_from_center_in=radius,
                )
                for angle, diameter, radius in self.lid_port_panel.rows()
            ),
        )

    def update_preview(self) -> None:
        if self._suppress_preview_updates:
            return
        try:
            layout = self.read_layout()
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return

        render_cross_section(
            self.cross_section_scene,
            build_cross_section_preview(layout),
        )
        render_plan(self.plan_scene, build_plan_preview(layout))
        self.cross_section_view.sync_to_scene()
        self.plan_view.sync_to_scene()
        self.status_label.setText(
            f"Outer diameter: {layout.outer_diameter_in:.2f} in | "
            f"Full height: {layout.full_height_in:.2f} in | "
            f"Ports: {len(layout.side_ports)} side, {len(layout.lid_ports)} lid"
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

    def _prompt_add_side_port(self) -> None:
        dialog = PortValueDialog(
            "Add Side Port",
            (
                PortFieldSpec("Clock angle (deg)", 0.0, 0.0, 360.0),
                PortFieldSpec("Diameter (in)", 3.0, 0.1, 100.0),
                PortFieldSpec("Height above glass (in)", 4.0, 0.0, 250.0),
            ),
            self,
        )
        if dialog.exec():
            angle, diameter, height = dialog.values()
            self.add_side_port(
                VesselSidePort(
                    clock_angle_degrees=angle,
                    diameter_in=diameter,
                    height_above_glass_surface_in=height,
                )
            )

    def _prompt_add_lid_port(self) -> None:
        dialog = PortValueDialog(
            "Add Lid Port",
            (
                PortFieldSpec("Clock angle (deg)", 0.0, 0.0, 360.0),
                PortFieldSpec("Diameter (in)", 4.0, 0.1, 100.0),
                PortFieldSpec("Distance from center (in)", 8.0, 0.0, 500.0),
            ),
            self,
        )
        if dialog.exec():
            angle, diameter, radius = dialog.values()
            self.add_lid_port(
                VesselLidPort(
                    clock_angle_degrees=angle,
                    diameter_in=diameter,
                    radial_distance_from_center_in=radius,
                )
            )

    def _remove_selected_side_ports(self) -> None:
        self.side_port_panel.remove_selected_rows()
        self.update_preview()

    def _remove_selected_lid_ports(self) -> None:
        self.lid_port_panel.remove_selected_rows()
        self.update_preview()

    def _build_preview_panel(
        self,
        title: str,
        view: ZoomableGraphicsView,
    ) -> QWidget:
        title_label = QLabel(title)
        zoom_in_button = QPushButton("+")
        zoom_in_button.clicked.connect(view.zoom_in)
        zoom_out_button = QPushButton("-")
        zoom_out_button.clicked.connect(view.zoom_out)
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(view.reset_zoom)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(zoom_out_button)
        header_layout.addWidget(zoom_in_button)
        header_layout.addWidget(reset_button)

        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.addLayout(header_layout)
        panel_layout.addWidget(view, 1)
        return panel


def launch() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = VesselDrafterWindow()
    window.show()
    return app.exec()
