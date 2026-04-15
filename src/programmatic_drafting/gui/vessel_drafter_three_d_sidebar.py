"""3D-preview sidebar widget for the vessel drafter GUI.

The sidebar bundles the layer-visibility checkboxes, section-cut controls,
the reset-view button, and the material summary table that sit alongside the
3D canvas. It exposes its constituent widgets as public attributes so the
main window can wire signals and read state without reaching into private
state.
"""

from __future__ import annotations

from collections.abc import Iterable

from PyQt6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from programmatic_drafting.gui.material_summary_table import MaterialSummaryTable
from programmatic_drafting.gui.vessel_drafter_port_panel import make_double_spin
from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)

_LAYER_LABELS: tuple[str, ...] = (
    "glass_bath",
    "hot_face_refractory",
    "ifb",
    "duraboard",
    "steel_shell",
    "electrodes",
)


def _build_layer_visibility_checkboxes(
    labels: Iterable[str] = _LAYER_LABELS,
) -> dict[str, QCheckBox]:
    """Build the per-material visibility checkboxes keyed by layer label."""
    materials = DEFAULT_VESSEL_DRAFTER_LAYOUT.material_properties_by_name
    checkboxes: dict[str, QCheckBox] = {}
    for label in labels:
        checkbox = QCheckBox(materials[label].display_name)
        checkbox.setChecked(True)
        checkboxes[label] = checkbox
    return checkboxes


def _build_section_cut_angle_spin() -> QDoubleSpinBox:
    """Build the disabled-by-default section-cut angle spinner."""
    spin = make_double_spin(0.0, 0.0, 360.0)
    spin.setSingleStep(15.0)
    spin.setEnabled(False)
    return spin


class VesselThreeDSidebar(QWidget):
    """Sidebar that groups 3D-preview controls next to the canvas."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.reset_view_button = QPushButton("Reset 3D View")
        self.layer_visibility_checkboxes = _build_layer_visibility_checkboxes()
        self.section_cut_checkbox = QCheckBox("Split on vertical plane")
        self.section_cut_angle_spin = _build_section_cut_angle_spin()
        self.material_summary_table = MaterialSummaryTable(self)

        layout = QVBoxLayout(self)
        instructions = QLabel(
            "Drag to rotate the model. Use the checkboxes to hide layers."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        layout.addWidget(self.reset_view_button)
        layout.addWidget(self._build_layer_visibility_panel())
        layout.addWidget(self._build_section_cut_panel())
        layout.addWidget(QLabel("Material Summary"))
        layout.addWidget(self.material_summary_table)
        layout.addStretch(1)
        self.setMinimumWidth(360)

    def _build_layer_visibility_panel(self) -> QWidget:
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.addWidget(QLabel("Visible Layers"))
        for checkbox in self.layer_visibility_checkboxes.values():
            panel_layout.addWidget(checkbox)
        panel_layout.addStretch(1)
        return panel

    def _build_section_cut_panel(self) -> QWidget:
        panel = QWidget()
        panel_layout = QFormLayout(panel)
        panel_layout.addRow(self.section_cut_checkbox)
        panel_layout.addRow("Split angle (deg)", self.section_cut_angle_spin)
        return panel

    def visible_layer_labels(self) -> set[str]:
        """Return the set of layer labels currently marked visible."""
        return {
            label
            for label, checkbox in self.layer_visibility_checkboxes.items()
            if checkbox.isChecked()
        }

    def read_view_options(self) -> Vessel3DViewOptions:
        """Return the current 3D view-option values from the sidebar controls."""
        return Vessel3DViewOptions(
            split_enabled=self.section_cut_checkbox.isChecked(),
            split_angle_degrees=self.section_cut_angle_spin.value(),
        )
