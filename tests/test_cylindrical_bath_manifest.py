from __future__ import annotations

import pytest

from programmatic_drafting.models.cylindrical_bath import (
    DEFAULT_CYLINDRICAL_BATH_LAYOUT,
    _build_bath_manifest,
    _build_drafting_manifest,
    _build_electrodes_manifest,
    _build_placement_manifest,
)


def test_bath_manifest_reports_inner_and_outer_geometry() -> None:
    manifest = _build_bath_manifest(DEFAULT_CYLINDRICAL_BATH_LAYOUT.bath)

    assert manifest["shape"] == "cylindrical"
    assert manifest["inner_diameter_in"] == pytest.approx(50.0)
    assert manifest["outer_diameter_in"] == pytest.approx(62.0)


def test_electrodes_manifest_reports_modeled_length() -> None:
    manifest = _build_electrodes_manifest(DEFAULT_CYLINDRICAL_BATH_LAYOUT.electrodes)

    assert manifest["count"] == 3
    assert manifest["modeled_length_in"] == pytest.approx(50.0)
    assert manifest["center_height_fraction"] == pytest.approx(0.5)


def test_drafting_manifest_documents_reference_assumptions() -> None:
    manifest = _build_drafting_manifest()

    assert manifest["axis_convention"] == "Z up"
    assert manifest["electrodes_centered_vertically"] is True


def test_placement_manifest_reports_radial_points() -> None:
    manifest = _build_placement_manifest(DEFAULT_CYLINDRICAL_BATH_LAYOUT.placements[0])

    assert manifest["index"] == 1
    assert len(manifest["center_mm"]) == 3
    assert len(manifest["inner_tip_mm"]) == 3
    assert len(manifest["outer_tip_mm"]) == 3
