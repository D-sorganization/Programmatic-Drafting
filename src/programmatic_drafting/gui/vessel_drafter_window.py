"""PyQt6 GUI for the vessel drafter tool."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QTabWidget,
)

from programmatic_drafting.analysis.vessel_drafter_metrics import (
    build_material_metrics_report,
)
from programmatic_drafting.exporters.step_export import export_vessel_drafter_step
from programmatic_drafting.gui.vessel_drafter_port_prompts import (
    prompt_add_lid_port,
    prompt_add_side_port,
)
from programmatic_drafting.gui.vessel_drafter_rendering import (
    render_cross_section,
    render_plan,
)
from programmatic_drafting.gui.vessel_drafter_window_controls import (
    build_dimension_controls,
    build_electrode_controls,
    build_port_panels,
    build_preview_tabs,
    build_preview_widgets,
    build_ui,
    dimension_controls,
)
from programmatic_drafting.gui.vessel_drafter_window_layout_io import (
    add_lid_port_to_controls,
    add_side_port_to_controls,
    read_layout_from_controls,
    write_layout_to_controls,
)
from programmatic_drafting.gui.vessel_drafter_window_status import (
    format_status_text as _format_status_text,
)
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
        build_dimension_controls(self)

    def _build_electrode_controls(self) -> None:
        build_electrode_controls(self)

    def _build_port_panels(self) -> None:
        build_port_panels(self)

    def _build_preview_widgets(self) -> None:
        build_preview_widgets(self)

    def _build_ui(self) -> None:
        build_ui(self)

    def _connect_signals(self) -> None:
        self._connect_dimension_signals()
        self._connect_port_panel_signals()
        self._connect_preview_signals()

    def _dimension_controls(self) -> tuple:
        return dimension_controls(self)

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
        write_layout_to_controls(self, layout)

    def add_side_port(self, port: VesselSidePort) -> None:
        add_side_port_to_controls(self, port)
        self.update_preview()

    def add_lid_port(self, port: VesselLidPort) -> None:
        add_lid_port_to_controls(self, port)
        self.update_preview()

    def read_layout(self) -> VesselDrafterLayout:
        return read_layout_from_controls(self)

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
        return build_preview_tabs(self)

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
