from __future__ import annotations

import pytest

from programmatic_drafting.models.electrode_advisor import (
    DEFAULT_ELECTRODE_ADVISOR_LAYOUT,
    _build_bath_manifest,
    _build_drafting_manifest,
    _build_electrodes_manifest,
    _build_placement_manifest,
    _build_source_viewer_manifest,
)


def test_source_viewer_manifest_tracks_ui_sources() -> None:
    manifest = _build_source_viewer_manifest()

    assert manifest["component"].endswith("GlassBath3DViewer.tsx")
    assert manifest["calculator"].endswith("ElectrodeAdvisorCalculator.tsx")


def test_bath_manifest_reports_default_geometry() -> None:
    manifest = _build_bath_manifest(DEFAULT_ELECTRODE_ADVISOR_LAYOUT.bath)

    assert manifest["shape"] == "rectangular"
    assert manifest["width_m"] == pytest.approx(3.0)
    assert manifest["glass_level_m"] == pytest.approx(1.5)


def test_electrodes_manifest_reports_current_and_dimensions() -> None:
    manifest = _build_electrodes_manifest(DEFAULT_ELECTRODE_ADVISOR_LAYOUT.electrodes)

    assert manifest["count"] == 3
    assert manifest["diameter_mm"] == pytest.approx(150.0)
    assert manifest["operating_current_a"] == pytest.approx(2500.0)


def test_drafting_manifest_reports_assumptions() -> None:
    manifest = _build_drafting_manifest(DEFAULT_ELECTRODE_ADVISOR_LAYOUT.drafting)

    assert manifest["bath_shell_thickness_mm"] == pytest.approx(25.0)
    assert manifest["electrode_holder_radius_factor"] == pytest.approx(2.0)


def test_placement_manifest_reports_viewer_and_cad_positions() -> None:
    placement = _build_placement_manifest(
        DEFAULT_ELECTRODE_ADVISOR_LAYOUT.placements[0]
    )

    assert placement["index"] == 1
    assert len(placement["viewer_position_m"]) == 3
    assert len(placement["cad_position_mm"]) == 3
