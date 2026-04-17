"""Structural guardrails for vessel scene test modules."""

from __future__ import annotations

from pathlib import Path


def test_vessel_drafter_scene_test_modules_stay_focused() -> None:
    tests_dir = Path(__file__).parent
    scene_tests = tests_dir.glob("test_vessel_drafter_scene*.py")

    oversized = {
        path.name: len(path.read_text(encoding="utf-8").splitlines())
        for path in scene_tests
        if path.name != Path(__file__).name
        and len(path.read_text(encoding="utf-8").splitlines()) > 300
    }

    assert oversized == {}
