from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

from programmatic_drafting import cli


@pytest.mark.parametrize(
    ("command", "export_name", "expected_prefix", "expected_filename"),
    [
        (
            "export-electrode-advisor-default",
            "export_default_layout_step",
            "Exported electrode advisor STEP artifact to ",
            "electrode.step",
        ),
        (
            "export-cylindrical-bath-layout",
            "export_cylindrical_bath_layout_step",
            "Exported cylindrical bath STEP artifact to ",
            "cylindrical.step",
        ),
        (
            "export-vessel-drafter-default",
            "export_vessel_drafter_default_step",
            "Exported vessel drafter STEP artifact to ",
            "vessel.step",
        ),
    ],
)
def test_main_logs_exported_step_path(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    command: str,
    export_name: str,
    expected_prefix: str,
    expected_filename: str,
    tmp_path: Path,
) -> None:
    def fake_export(output_path, manifest_path):
        return tmp_path / f"{output_path.stem.split('_')[0]}.step"

    monkeypatch.setattr(
        cli,
        export_name,
        fake_export,
    )
    monkeypatch.setattr(sys, "argv", ["programmatic-drafting", command])

    caplog.set_level(logging.INFO, logger="programmatic_drafting.cli")

    assert cli.main() == 0
    expected_message = f"{expected_prefix}{tmp_path / expected_filename}"
    assert expected_message in caplog.text
