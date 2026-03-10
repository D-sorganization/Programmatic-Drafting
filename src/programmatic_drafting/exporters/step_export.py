"""STEP export utilities."""

from __future__ import annotations

import json
from pathlib import Path

from build123d import export_step

from programmatic_drafting.models.electrode_advisor import (
    DEFAULT_ELECTRODE_ADVISOR_LAYOUT,
    ElectrodeAdvisorLayout,
)
from programmatic_drafting.projects.electrode_advisor_default_layout import (
    build_default_layout_shape,
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
