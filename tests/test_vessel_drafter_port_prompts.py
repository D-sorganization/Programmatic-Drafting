"""Tests for the side/lid port prompt dialog helpers."""

import os

import pytest
from PyQt6.QtWidgets import QApplication, QWidget

from programmatic_drafting.gui import vessel_drafter_port_prompts
from programmatic_drafting.gui.vessel_drafter_port_prompts import (
    prompt_add_lid_port,
    prompt_add_side_port,
)
from programmatic_drafting.models.vessel_drafter import (
    VesselLidPort,
    VesselSidePort,
)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    assert isinstance(app, QApplication)
    return app


class _FakeDialog:
    """Stand-in for ``PortValueDialog`` that bypasses Qt's modal exec loop."""

    def __init__(self, accept: bool, values: tuple[float, float, float]) -> None:
        self._accept = accept
        self._values = values

    def __call__(self, *_args: object, **_kwargs: object) -> "_FakeDialog":
        return self

    def exec(self) -> int:
        return 1 if self._accept else 0

    def values(self) -> tuple[float, float, float]:
        return self._values


def test_prompt_add_side_port_returns_none_when_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _ensure_app()
    parent = QWidget()
    try:
        monkeypatch.setattr(
            vessel_drafter_port_prompts,
            "PortValueDialog",
            _FakeDialog(accept=False, values=(0.0, 0.0, 0.0)),
        )
        assert prompt_add_side_port(parent) is None
    finally:
        parent.deleteLater()
        app.processEvents()


def test_prompt_add_side_port_returns_port_when_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _ensure_app()
    parent = QWidget()
    try:
        monkeypatch.setattr(
            vessel_drafter_port_prompts,
            "PortValueDialog",
            _FakeDialog(accept=True, values=(45.0, 2.5, 7.0)),
        )
        port = prompt_add_side_port(parent)
        assert isinstance(port, VesselSidePort)
        assert port.clock_angle_degrees == pytest.approx(45.0)
        assert port.diameter_in == pytest.approx(2.5)
        assert port.height_above_glass_surface_in == pytest.approx(7.0)
    finally:
        parent.deleteLater()
        app.processEvents()


def test_prompt_add_lid_port_returns_port_when_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _ensure_app()
    parent = QWidget()
    try:
        monkeypatch.setattr(
            vessel_drafter_port_prompts,
            "PortValueDialog",
            _FakeDialog(accept=True, values=(90.0, 3.0, 8.5)),
        )
        port = prompt_add_lid_port(parent)
        assert isinstance(port, VesselLidPort)
        assert port.clock_angle_degrees == pytest.approx(90.0)
        assert port.diameter_in == pytest.approx(3.0)
        assert port.radial_distance_from_center_in == pytest.approx(8.5)
    finally:
        parent.deleteLater()
        app.processEvents()


def test_prompt_add_lid_port_returns_none_when_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _ensure_app()
    parent = QWidget()
    try:
        monkeypatch.setattr(
            vessel_drafter_port_prompts,
            "PortValueDialog",
            _FakeDialog(accept=False, values=(0.0, 0.0, 0.0)),
        )
        assert prompt_add_lid_port(parent) is None
    finally:
        parent.deleteLater()
        app.processEvents()
