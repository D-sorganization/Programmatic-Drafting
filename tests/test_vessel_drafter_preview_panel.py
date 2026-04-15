"""Tests for the reusable zoomable preview-panel widget."""

import os

import pytest
from PyQt6.QtWidgets import QApplication

from programmatic_drafting.gui.vessel_drafter_preview_panel import PreviewPanel
from programmatic_drafting.gui.zoomable_graphics_view import ZoomableGraphicsView

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    assert isinstance(app, QApplication)
    return app


def test_preview_panel_hosts_provided_view() -> None:
    app = _ensure_app()
    view = ZoomableGraphicsView()
    panel = PreviewPanel("Cross-Section Preview", view)
    try:
        assert panel.view is view
    finally:
        panel.deleteLater()
        app.processEvents()


def test_preview_panel_zoom_buttons_invoke_view_zoom_controls() -> None:
    app = _ensure_app()
    view = ZoomableGraphicsView()
    panel = PreviewPanel("Top View Preview", view)
    try:
        assert view.zoom_factor == pytest.approx(1.0)

        panel._zoom_in_button.click()
        assert view.zoom_factor > 1.0

        panel._zoom_out_button.click()
        panel._zoom_out_button.click()
        assert view.zoom_factor < 1.0

        panel._reset_button.click()
        assert view.zoom_factor == pytest.approx(1.0)
    finally:
        panel.deleteLater()
        app.processEvents()
