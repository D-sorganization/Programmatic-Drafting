"""Tests for the 3D-preview sidebar widget extracted from the window module."""

import os

import pytest
from PyQt6.QtWidgets import QApplication

from programmatic_drafting.gui.vessel_drafter_three_d_sidebar import (
    VesselThreeDSidebar,
)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _ensure_app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_sidebar_exposes_expected_layer_checkboxes() -> None:
    app = _ensure_app()
    sidebar = VesselThreeDSidebar()
    try:
        labels = set(sidebar.layer_visibility_checkboxes)
        assert labels == {
            "glass_bath",
            "hot_face_refractory",
            "ifb",
            "duraboard",
            "steel_shell",
            "electrodes",
        }
        assert all(
            checkbox.isChecked()
            for checkbox in sidebar.layer_visibility_checkboxes.values()
        )
    finally:
        sidebar.deleteLater()
        app.processEvents()


def test_sidebar_visible_layer_labels_tracks_checkbox_state() -> None:
    app = _ensure_app()
    sidebar = VesselThreeDSidebar()
    try:
        assert "steel_shell" in sidebar.visible_layer_labels()
        sidebar.layer_visibility_checkboxes["steel_shell"].setChecked(False)
        assert "steel_shell" not in sidebar.visible_layer_labels()
    finally:
        sidebar.deleteLater()
        app.processEvents()


def test_sidebar_section_cut_defaults_disable_angle_spin() -> None:
    app = _ensure_app()
    sidebar = VesselThreeDSidebar()
    try:
        assert not sidebar.section_cut_checkbox.isChecked()
        assert not sidebar.section_cut_angle_spin.isEnabled()
        assert sidebar.section_cut_angle_spin.maximum() == pytest.approx(360.0)
    finally:
        sidebar.deleteLater()
        app.processEvents()


def test_sidebar_read_view_options_reflects_controls() -> None:
    app = _ensure_app()
    sidebar = VesselThreeDSidebar()
    try:
        options = sidebar.read_view_options()
        assert options.split_enabled is False
        assert options.split_angle_degrees == pytest.approx(0.0)

        sidebar.section_cut_checkbox.setChecked(True)
        sidebar.section_cut_angle_spin.setValue(90.0)
        options = sidebar.read_view_options()
        assert options.split_enabled is True
        assert options.split_angle_degrees == pytest.approx(90.0)
    finally:
        sidebar.deleteLater()
        app.processEvents()
