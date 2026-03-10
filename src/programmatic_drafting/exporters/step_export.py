"""STEP export utilities."""

from __future__ import annotations

import json
from pathlib import Path

from build123d import export_step

from programmatic_drafting.models.cylindrical_bath import (
    DEFAULT_CYLINDRICAL_BATH_LAYOUT,
    CylindricalBathLayout,
)
from programmatic_drafting.models.electrode_advisor import (
    DEFAULT_ELECTRODE_ADVISOR_LAYOUT,
    ElectrodeAdvisorLayout,
)
from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    VesselDrafterLayout,
)
from programmatic_drafting.projects.cylindrical_bath_layout import (
    build_cylindrical_bath_layout_shape,
)
from programmatic_drafting.projects.electrode_advisor_default_layout import (
    build_default_layout_shape,
)
from programmatic_drafting.projects.vessel_drafter_layout import (
    build_vessel_drafter_shape,
)


def export_default_layout_step(
    output_path: Path,
    manifest_path: Path | None = None,
    layout: ElectrodeAdvisorLayout = DEFAULT_ELECTRODE_ADVISOR_LAYOUT,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shape = build_default_layout_shape(layout)
    export_step(shape, output_path)

    if manifest_path is not None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(layout.to_manifest(), indent=2) + "\n",
            encoding="utf-8",
        )

    return output_path


def export_cylindrical_bath_layout_step(
    output_path: Path,
    manifest_path: Path | None = None,
    layout: CylindricalBathLayout = DEFAULT_CYLINDRICAL_BATH_LAYOUT,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shape = build_cylindrical_bath_layout_shape(layout)
    export_step(shape, output_path)

    if manifest_path is not None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(layout.to_manifest(), indent=2) + "\n",
            encoding="utf-8",
        )

    return output_path


def export_vessel_drafter_step(
    output_path: Path,
    manifest_path: Path | None = None,
    layout: VesselDrafterLayout = DEFAULT_VESSEL_DRAFTER_LAYOUT,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shape = build_vessel_drafter_shape(layout)
    export_step(shape, output_path)

    if manifest_path is not None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(layout.to_manifest(), indent=2) + "\n",
            encoding="utf-8",
        )

    return output_path


def export_vessel_drafter_default_step(
    output_path: Path,
    manifest_path: Path | None = None,
) -> Path:
    return export_vessel_drafter_step(
        output_path=output_path,
        manifest_path=manifest_path,
        layout=DEFAULT_VESSEL_DRAFTER_LAYOUT,
    )
