"""Widget construction helpers for the vessel drafter main window."""

from __future__ import annotations

from typing import Any

from PyQt6.QtWidgets import (
    QFormLayout,
    QGraphicsScene,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from programmatic_drafting.gui.vessel_drafter_port_panel import (
    PortTableSection,
    make_double_spin,
)
from programmatic_drafting.gui.vessel_drafter_preview_panel import PreviewPanel
from programmatic_drafting.gui.vessel_drafter_three_d_canvas import (
    VesselDrafterThreeDCanvas,
)
from programmatic_drafting.gui.vessel_drafter_three_d_sidebar import (
    VesselThreeDSidebar,
)
from programmatic_drafting.gui.zoomable_graphics_view import ZoomableGraphicsView


def build_dimension_controls(window: Any) -> None:
    """Create vessel dimension controls on ``window``."""
    window.inner_diameter_spin = make_double_spin(50.0, 1.0, 500.0)
    window.glass_depth_spin = make_double_spin(14.0, 1.0, 250.0)
    window.plenum_height_spin = make_double_spin(14.0, 1.0, 250.0)
    window.head_depth_spin = make_double_spin(12.5, 1.0, 250.0)
    window.hot_face_spin = make_double_spin(6.0, 0.1, 50.0)
    window.ifb_spin = make_double_spin(4.5, 0.1, 50.0)
    window.duraboard_spin = make_double_spin(1.0, 0.1, 20.0)
    window.steel_spin = make_double_spin(0.5, 0.1, 10.0)


def build_electrode_controls(window: Any) -> None:
    """Create electrode parameter controls on ``window``."""
    window.electrode_count_spin = QSpinBox()
    window.electrode_count_spin.setRange(1, 12)
    window.electrode_count_spin.setValue(3)
    window.electrode_diameter_spin = make_double_spin(2.0, 0.1, 20.0)
    window.electrode_insertion_spin = make_double_spin(14.0, 0.1, 100.0)
    window.electrode_extension_spin = make_double_spin(36.0, 0.1, 150.0)


def build_port_panels(window: Any) -> None:
    """Create editable side and lid port panels on ``window``."""
    window.side_port_panel = PortTableSection(
        "Side Ports",
        ("Clock Angle", "Diameter", "Height Above Glass"),
    )
    window.lid_port_panel = PortTableSection(
        "Lid Ports",
        ("Clock Angle", "Diameter", "Distance From Center"),
    )


def build_preview_widgets(window: Any) -> None:
    """Create preview scenes, views, canvas, and sidebar widgets."""
    window.cross_section_scene = QGraphicsScene(window)
    window.cross_section_view = ZoomableGraphicsView(window)
    window.cross_section_view.setScene(window.cross_section_scene)
    window.plan_scene = QGraphicsScene(window)
    window.plan_view = ZoomableGraphicsView(window)
    window.plan_view.setScene(window.plan_scene)
    window.preview_tabs = QTabWidget(window)
    window.three_d_canvas = VesselDrafterThreeDCanvas()
    window.three_d_sidebar = VesselThreeDSidebar()
    window.layer_visibility_checkboxes = (
        window.three_d_sidebar.layer_visibility_checkboxes
    )
    window.section_cut_checkbox = window.three_d_sidebar.section_cut_checkbox
    window.section_cut_angle_spin = window.three_d_sidebar.section_cut_angle_spin
    window.material_summary_table = window.three_d_sidebar.material_summary_table
    window.status_label = QLabel()
    window.status_label.setWordWrap(True)


def build_ui(window: Any) -> None:
    """Build the main two-column window layout."""
    root = QWidget()
    window.setCentralWidget(root)

    controls_scroll = build_controls_scroll_area(window)
    preview_layout = QVBoxLayout()
    preview_layout.addWidget(build_preview_tabs(window), 1)

    main_layout = QHBoxLayout(root)
    main_layout.addWidget(controls_scroll, 0)
    main_layout.addLayout(preview_layout, 1)


def build_controls_form(window: Any) -> QFormLayout:
    """Build the static vessel/electrode controls form."""
    controls_form = QFormLayout()
    controls_form.addRow("Inner diameter (in)", window.inner_diameter_spin)
    controls_form.addRow("Glass depth (in)", window.glass_depth_spin)
    controls_form.addRow("Plenum height (in)", window.plenum_height_spin)
    controls_form.addRow("Head depth (in)", window.head_depth_spin)
    controls_form.addRow("Hot face (in)", window.hot_face_spin)
    controls_form.addRow("IFB (in)", window.ifb_spin)
    controls_form.addRow("Duraboard (in)", window.duraboard_spin)
    controls_form.addRow("Steel (in)", window.steel_spin)
    controls_form.addRow("Electrode count", window.electrode_count_spin)
    controls_form.addRow("Electrode diameter (in)", window.electrode_diameter_spin)
    controls_form.addRow("Electrode insertion (in)", window.electrode_insertion_spin)
    controls_form.addRow("Electrode extension (in)", window.electrode_extension_spin)
    return controls_form


def build_action_buttons(window: Any) -> tuple[QPushButton, QPushButton]:
    """Create command buttons and wire their click handlers."""
    window.refresh_button = QPushButton("Refresh Preview")
    window.refresh_button.clicked.connect(window.update_preview)
    window.export_button = QPushButton("Export STEP")
    window.export_button.clicked.connect(window.export_step_dialog)
    return window.refresh_button, window.export_button


def build_controls_scroll_area(window: Any) -> QScrollArea:
    """Build the scrollable left-side controls column."""
    refresh_button, export_button = build_action_buttons(window)
    controls_root = QWidget()
    controls_layout = QVBoxLayout(controls_root)
    controls_layout.addLayout(build_controls_form(window))
    controls_layout.addWidget(window.side_port_panel)
    controls_layout.addWidget(window.lid_port_panel)
    controls_layout.addWidget(refresh_button)
    controls_layout.addWidget(export_button)
    controls_layout.addWidget(window.status_label)
    controls_layout.addStretch(1)

    controls_scroll = QScrollArea()
    controls_scroll.setWidgetResizable(True)
    controls_scroll.setWidget(controls_root)
    controls_scroll.setMinimumWidth(340)
    return controls_scroll


def dimension_controls(window: Any) -> tuple[Any, ...]:
    """Return controls whose value changes refresh the 2D previews."""
    return (
        window.inner_diameter_spin,
        window.glass_depth_spin,
        window.plenum_height_spin,
        window.head_depth_spin,
        window.hot_face_spin,
        window.ifb_spin,
        window.duraboard_spin,
        window.steel_spin,
        window.electrode_count_spin,
        window.electrode_diameter_spin,
        window.electrode_insertion_spin,
        window.electrode_extension_spin,
    )


def build_preview_tabs(window: Any) -> QTabWidget:
    """Build the tabbed 2D and 3D preview area."""
    previews_tab = QWidget()
    previews_layout = QVBoxLayout(previews_tab)
    previews_layout.addWidget(
        PreviewPanel("Cross-Section Preview", window.cross_section_view),
        1,
    )
    previews_layout.addWidget(
        PreviewPanel("Top View Preview", window.plan_view),
        1,
    )

    three_d_tab = QWidget()
    three_d_layout = QHBoxLayout(three_d_tab)
    three_d_layout.addWidget(window.three_d_canvas, 1)
    three_d_layout.addWidget(window.three_d_sidebar, 0)

    window.preview_tabs.addTab(previews_tab, "2D Previews")
    window.preview_tabs.addTab(three_d_tab, "3D Preview")
    return window.preview_tabs
