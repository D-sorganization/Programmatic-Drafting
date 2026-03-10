import os

import pytest
from PyQt6.QtWidgets import QApplication

from programmatic_drafting.gui.vessel_drafter_window import VesselDrafterWindow
from programmatic_drafting.models.vessel_drafter import VesselLidPort, VesselSidePort

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
