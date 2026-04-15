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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from programmatic_drafting.analysis.vessel_drafter_metrics import (
    MaterialMetricsReport,
    build_material_metrics_report,
)
from programmatic_drafting.exporters.step_export import export_vessel_drafter_step
from programmatic_drafting.gui.vessel_drafter_port_panel import (
    PortTableSection,
    make_double_spin,
)
from programmatic_drafting.gui.vessel_drafter_port_prompts import (
    prompt_add_lid_port,
    prompt_add_side_port,
)
from programmatic_drafting.gui.vessel_drafter_preview_panel import PreviewPanel
from programmatic_drafting.gui.vessel_drafter_rendering import (
    render_cross_section,
    render_plan,
)
from programmatic_drafting.gui.vessel_drafter_three_d_canvas import (
    VesselDrafterThreeDCanvas,
)
from programmatic_drafting.gui.vessel_drafter_three_d_sidebar import (
    VesselThreeDSidebar,
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
from programmatic_drafting.preview.vessel_drafter_scene import build_vessel_3d_scene


class VesselDrafterWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._configure_window()
        self._suppress_preview_updates = False
        self._three_d_preview_dirty = True
        self._build_dimension_controls()
        self._build_electrode_controls()
        self._build_port_panels()
        self._build_preview_widgets()
        self._build_ui()
        self._connect_signals()
        self.write_layout(DEFAULT_VESSEL_DRAFTER_LAYOUT)
        self.update_preview()

    def _configure_window(self) -> None:
        """Apply static top-level window settings."""
        self.setWindowTitle("Vessel Drafter")
        self.resize(1400, 880)

    def _build_dimension_controls(self) -> None:
        """Create vessel dimension controls."""
        self.inner_diameter_spin = make_double_spin(50.0, 1.0, 500.0)
        self.glass_depth_spin = make_double_spin(14.0, 1.0, 250.0)
        self.plenum_height_spin = make_double_spin(14.0, 1.0, 250.0)
        self.head_depth_spin = make_double_spin(12.5, 1.0, 250.0)
        self.hot_face_spin = make_double_spin(6.0, 0.1, 50.0)
        self.ifb_spin = make_double_spin(4.5, 0.1, 50.0)
        self.duraboard_spin = make_double_spin(1.0, 0.1, 20.0)
        self.steel_spin = make_double_spin(0.5, 0.1, 10.0)

    def _build_electrode_controls(self) -> None:
        """Create electrode parameter controls."""
        self.electrode_count_spin = QSpinBox()
        self.electrode_count_spin.setRange(1, 12)
        self.electrode_count_spin.setValue(3)
        self.electrode_diameter_spin = make_double_spin(2.0, 0.1, 20.0)
        self.electrode_insertion_spin = make_double_spin(14.0, 0.1, 100.0)
        self.electrode_extension_spin = make_double_spin(36.0, 0.1, 150.0)

    def _build_port_panels(self) -> None:
        """Create editable side and lid port panels."""
        self.side_port_panel = PortTableSection(
            "Side Ports",
            ("Clock Angle", "Diameter", "Height Above Glass"),
        )
        self.lid_port_panel = PortTableSection(
            "Lid Ports",
            ("Clock Angle", "Diameter", "Distance From Center"),
        )

    def _build_preview_widgets(self) -> None:
        """Create preview scenes, views, canvas, and sidebar widgets."""
        self.cross_section_scene = QGraphicsScene(self)
        self.cross_section_view = ZoomableGraphicsView(self)
        self.cross_section_view.setScene(self.cross_section_scene)
        self.plan_scene = QGraphicsScene(self)
        self.plan_view = ZoomableGraphicsView(self)
        self.plan_view.setScene(self.plan_scene)
        self.preview_tabs = QTabWidget(self)
        self.three_d_canvas = VesselDrafterThreeDCanvas()
        self.three_d_sidebar = VesselThreeDSidebar()
        # Expose sidebar sub-widgets for backward compatibility with callers
        # and tests that reach them through the window.
        self.layer_visibility_checkboxes = (
            self.three_d_sidebar.layer_visibility_checkboxes
        )
        self.section_cut_checkbox = self.three_d_sidebar.section_cut_checkbox
        self.section_cut_angle_spin = self.three_d_sidebar.section_cut_angle_spin
        self.material_summary_table = self.three_d_sidebar.material_summary_table
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        controls_scroll = self._build_controls_scroll_area()
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self._build_preview_tabs(), 1)

        main_layout = QHBoxLayout(root)
        main_layout.addWidget(controls_scroll, 0)
        main_layout.addLayout(preview_layout, 1)

    def _build_controls_form(self) -> QFormLayout:
        """Build the static vessel/electrode controls form."""
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
        return controls_form

    def _build_action_buttons(self) -> tuple[QPushButton, QPushButton]:
        """Create command buttons and wire their click handlers."""
        self.refresh_button = QPushButton("Refresh Preview")
        self.refresh_button.clicked.connect(self.update_preview)
        self.export_button = QPushButton("Export STEP")
        self.export_button.clicked.connect(self.export_step_dialog)
        return self.refresh_button, self.export_button

    def _build_controls_scroll_area(self) -> QScrollArea:
        """Build the scrollable left-side controls column."""
        refresh_button, export_button = self._build_action_buttons()
        controls_root = QWidget()
        controls_layout = QVBoxLayout(controls_root)
        controls_layout.addLayout(self._build_controls_form())
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
        return controls_scroll

    def _connect_signals(self) -> None:
        self._connect_dimension_signals()
        self._connect_port_panel_signals()
        self._connect_preview_signals()

    def _dimension_controls(self) -> tuple:
        """Return controls whose value changes refresh the 2D previews."""
        return (
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

    def _connect_dimension_signals(self) -> None:
        """Connect scalar dimension/electrode controls to preview refresh."""
        for widget in self._dimension_controls():
            widget.valueChanged.connect(self.update_preview)

    def _connect_port_panel_signals(self) -> None:
        """Connect port table controls to add/remove/refresh handlers."""
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

    def _connect_preview_signals(self) -> None:
        """Connect preview option controls to their 3D preview handlers."""
        for checkbox in self.layer_visibility_checkboxes.values():
            checkbox.toggled.connect(self.refresh_three_d_preview)
        self.section_cut_checkbox.toggled.connect(self._handle_section_cut_toggled)
        self.section_cut_angle_spin.valueChanged.connect(
            self._handle_section_cut_angle_changed
        )
        self.preview_tabs.currentChanged.connect(self._handle_preview_tab_changed)
        self.three_d_sidebar.reset_view_button.clicked.connect(
            self.three_d_canvas.reset_view
        )

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
        self._three_d_preview_dirty = True
        self._refresh_three_d_preview_if_visible(layout)
        metrics = build_material_metrics_report(layout)
        self.material_summary_table.set_report(metrics)
        self.cross_section_view.sync_to_scene()
        self.plan_view.sync_to_scene()
        self.status_label.setText(_format_status_text(layout, metrics))

    def refresh_three_d_preview(self) -> None:
        if self._suppress_preview_updates:
            return
        try:
            layout = self.read_layout()
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return
        self._three_d_preview_dirty = True
        self._refresh_three_d_preview_if_visible(layout)

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
        port = prompt_add_side_port(self)
        if port is not None:
            self.add_side_port(port)

    def _prompt_add_lid_port(self) -> None:
        port = prompt_add_lid_port(self)
        if port is not None:
            self.add_lid_port(port)

    def _remove_selected_side_ports(self) -> None:
        self.side_port_panel.remove_selected_rows()
        self.update_preview()

    def _remove_selected_lid_ports(self) -> None:
        self.lid_port_panel.remove_selected_rows()
        self.update_preview()

    def _build_preview_tabs(self) -> QTabWidget:
        previews_tab = QWidget()
        previews_layout = QVBoxLayout(previews_tab)
        previews_layout.addWidget(
            PreviewPanel("Cross-Section Preview", self.cross_section_view),
            1,
        )
        previews_layout.addWidget(
            PreviewPanel("Top View Preview", self.plan_view),
            1,
        )

        three_d_tab = QWidget()
        three_d_layout = QHBoxLayout(three_d_tab)
        three_d_layout.addWidget(self.three_d_canvas, 1)
        three_d_layout.addWidget(self.three_d_sidebar, 0)

        self.preview_tabs.addTab(previews_tab, "2D Previews")
        self.preview_tabs.addTab(three_d_tab, "3D Preview")
        return self.preview_tabs

    def _update_three_d_preview(self, layout: VesselDrafterLayout) -> None:
        view_options = self.three_d_sidebar.read_view_options()
        self.three_d_canvas.draw_scene(
            build_vessel_3d_scene(
                layout,
                visible_labels=self.three_d_sidebar.visible_layer_labels(),
                view_options=view_options,
            ),
            view_options,
        )
        self._three_d_preview_dirty = False

    def _handle_preview_tab_changed(self, index: int) -> None:
        if index != self.preview_tabs.indexOf(self.preview_tabs.widget(1)):
            return
        self.refresh_three_d_preview()

    def _refresh_three_d_preview_if_visible(self, layout: VesselDrafterLayout) -> None:
        if self._three_d_preview_dirty and self.preview_tabs.currentIndex() == 1:
            self._update_three_d_preview(layout)

    def _handle_section_cut_toggled(self, checked: bool) -> None:
        self.section_cut_angle_spin.setEnabled(checked)
        self.three_d_canvas.queue_default_view(self.three_d_sidebar.read_view_options())
        self.refresh_three_d_preview()

    def _handle_section_cut_angle_changed(self, _: float) -> None:
        if self.section_cut_checkbox.isChecked():
            self.three_d_canvas.queue_default_view(
                self.three_d_sidebar.read_view_options()
            )
        self.refresh_three_d_preview()


def launch() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = VesselDrafterWindow()
    window.show()
    return app.exec()


def _format_status_text(
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
