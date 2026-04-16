import os

import pytest
from PyQt6.QtWidgets import QApplication

from programmatic_drafting.analysis.vessel_drafter_metrics import MaterialMetricsReport
from programmatic_drafting.gui.vessel_drafter_window import (
    VesselDrafterWindow,
    _format_status_text,
)
from programmatic_drafting.gui.vessel_drafter_window_layout_io import (
    lid_port_rows,
    lid_ports_from_rows,
    read_layout_from_controls,
    side_port_rows,
    side_ports_from_rows,
    write_layout_to_controls,
)
from programmatic_drafting.gui.vessel_drafter_window_status import format_status_text
from programmatic_drafting.models.vessel_drafter import (
    VesselDrafterLayout,
    VesselLidPort,
    VesselSidePort,
)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_window_reads_defaults_and_refreshes_preview() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()
    window.show()
    app.processEvents()

    assert window.read_layout().inner_diameter_in == pytest.approx(50.0)
    base_scale = window.cross_section_view.transform().m11()

    window.inner_diameter_spin.setValue(60.0)
    updated_layout = window.read_layout()
    assert updated_layout.inner_diameter_in == pytest.approx(60.0)

    window.update_preview()
    assert "Outer diameter" in window.status_label.text()
    assert window.cross_section_view.transform().m11() == pytest.approx(base_scale)

    window.close()
    app.quit()


def test_window_round_trips_ports_without_manual_table_edits() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()
    window.show()
    app.processEvents()

    window.add_side_port(
        VesselSidePort(
            clock_angle_degrees=60.0,
            diameter_in=3.0,
            height_above_glass_surface_in=5.0,
        )
    )
    window.add_lid_port(
        VesselLidPort(
            clock_angle_degrees=90.0,
            diameter_in=4.0,
            radial_distance_from_center_in=9.0,
        )
    )

    layout = window.read_layout()

    assert len(layout.side_ports) == 1
    assert len(layout.lid_ports) == 1

    window.close()
    app.quit()


def test_preview_zoom_controls_preserve_user_zoom_across_refresh() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()
    window.show()
    app.processEvents()

    base_scale = window.cross_section_view.transform().m11()
    window.cross_section_view.zoom_in()
    zoomed_scale = window.cross_section_view.transform().m11()

    assert zoomed_scale > base_scale

    window.update_preview()
    refreshed_scale = window.cross_section_view.transform().m11()
    assert refreshed_scale == pytest.approx(zoomed_scale)

    window.cross_section_view.reset_zoom()
    reset_scale = window.cross_section_view.transform().m11()
    assert reset_scale == pytest.approx(base_scale)

    window.close()
    app.quit()


def test_window_exposes_three_d_preview_and_layer_controls() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()
    window.show()
    app.processEvents()

    assert window.preview_tabs.count() == 2
    assert window.preview_tabs.tabText(0) == "2D Previews"
    assert window.preview_tabs.tabText(1) == "3D Preview"
    assert "steel_shell" in window.layer_visibility_checkboxes
    assert window.material_summary_table.rowCount() >= 5
    assert not window.section_cut_checkbox.isChecked()

    window.preview_tabs.setCurrentIndex(1)
    app.processEvents()

    assert "steel_shell" in window.three_d_canvas.current_labels
    full_face_count = window.three_d_canvas.current_face_count

    window.section_cut_checkbox.setChecked(True)
    window.section_cut_angle_spin.setValue(45.0)
    app.processEvents()

    assert window.three_d_canvas.current_face_count < full_face_count
    assert window.three_d_canvas.view_state == pytest.approx((0.0, -45.0))

    window.layer_visibility_checkboxes["steel_shell"].setChecked(False)
    app.processEvents()

    assert "steel_shell" not in window.three_d_canvas.current_labels

    window.close()
    app.quit()


def test_window_initializes_control_groups() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()

    assert window.windowTitle() == "Vessel Drafter"
    assert window.inner_diameter_spin.maximum() == pytest.approx(500.0)
    assert window.electrode_count_spin.minimum() == 1
    assert window.electrode_count_spin.maximum() == 12
    assert window.side_port_panel.title() == "Side Ports"
    assert window.lid_port_panel.title() == "Lid Ports"
    assert window.cross_section_view.scene() is window.cross_section_scene
    assert window.plan_view.scene() is window.plan_scene
    assert window.refresh_button.text() == "Refresh Preview"
    assert window.export_button.text() == "Export STEP"
    assert window.status_label.wordWrap()
    assert len(window._dimension_controls()) == 12

    window.close()
    app.quit()


def test_section_cut_angle_changes_reset_three_d_view_to_section_plane() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()
    window.show()
    window.preview_tabs.setCurrentIndex(1)
    app.processEvents()

    window.section_cut_checkbox.setChecked(True)
    window.section_cut_angle_spin.setValue(120.0)
    app.processEvents()

    assert window.three_d_canvas.view_state == pytest.approx((0.0, 30.0))

    window.section_cut_angle_spin.setValue(270.0)
    app.processEvents()

    assert window.three_d_canvas.view_state == pytest.approx((0.0, -180.0))

    window.close()
    app.quit()


def test_format_status_text_summarizes_layout_and_metrics() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()
    layout = window.read_layout()
    metrics = MaterialMetricsReport(
        component_metrics=(),
        refractory_total_volume_in3=3456.0,
        refractory_total_volume_ft3=2.0,
        refractory_total_surface_area_ft2=3.5,
        refractory_total_mass_lb=456.7,
    )

    status = _format_status_text(layout, metrics)

    assert f"Outer diameter: {layout.outer_diameter_in:.2f} in" in status
    assert "Ports: 0 side, 0 lid" in status
    assert "Refractory: 2.00 ft^3, 3.50 ft^2, 456.7 lb" in status

    window.close()
    app.quit()


def test_port_row_helpers_round_trip_port_models() -> None:
    side_port = VesselSidePort(
        clock_angle_degrees=420.0,
        diameter_in=3.0,
        height_above_glass_surface_in=5.0,
    )
    lid_port = VesselLidPort(
        clock_angle_degrees=-90.0,
        diameter_in=4.0,
        radial_distance_from_center_in=9.0,
    )

    side_rows = side_port_rows((side_port,))
    lid_rows = lid_port_rows((lid_port,))

    assert side_rows == ((60.0, 3.0, 5.0),)
    assert lid_rows == ((270.0, 4.0, 9.0),)
    assert side_ports_from_rows(side_rows)[0].clock_angle_degrees == pytest.approx(60.0)
    assert lid_ports_from_rows(lid_rows)[0].clock_angle_degrees == pytest.approx(270.0)


def test_window_layout_io_helpers_round_trip_controls() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()
    layout = VesselDrafterLayout(
        inner_diameter_in=64.0,
        glass_depth_in=15.0,
        side_ports=(
            VesselSidePort(
                clock_angle_degrees=30.0,
                diameter_in=2.0,
                height_above_glass_surface_in=3.0,
            ),
        ),
        lid_ports=(
            VesselLidPort(
                clock_angle_degrees=120.0,
                diameter_in=3.0,
                radial_distance_from_center_in=8.0,
            ),
        ),
    )

    write_layout_to_controls(window, layout)
    read_back = read_layout_from_controls(window)

    assert window._suppress_preview_updates is False
    assert read_back.inner_diameter_in == pytest.approx(64.0)
    assert read_back.glass_depth_in == pytest.approx(15.0)
    assert read_back.side_ports[0].diameter_in == pytest.approx(2.0)
    assert read_back.lid_ports[0].radial_distance_from_center_in == pytest.approx(8.0)

    window.close()
    app.quit()


def test_status_module_matches_window_compatibility_alias() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()
    layout = window.read_layout()
    metrics = MaterialMetricsReport(
        component_metrics=(),
        refractory_total_volume_in3=1728.0,
        refractory_total_volume_ft3=1.0,
        refractory_total_surface_area_ft2=2.5,
        refractory_total_mass_lb=345.6,
    )

    assert _format_status_text(layout, metrics) == format_status_text(layout, metrics)

    window.close()
    app.quit()
