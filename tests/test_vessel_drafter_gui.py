import os

import pytest
from PyQt6.QtWidgets import QApplication

from programmatic_drafting.gui.vessel_drafter_window import VesselDrafterWindow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_window_reads_defaults_and_refreshes_preview() -> None:
    app = QApplication.instance() or QApplication([])
    window = VesselDrafterWindow()

    assert window.read_layout().inner_diameter_in == pytest.approx(50.0)

    window.inner_diameter_spin.setValue(60.0)
    updated_layout = window.read_layout()
    assert updated_layout.inner_diameter_in == pytest.approx(60.0)

    window.update_preview()
    assert "Outer diameter" in window.status_label.text()

    window.close()
    app.quit()
