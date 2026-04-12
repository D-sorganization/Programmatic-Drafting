"""3D preview scene builders for the vessel drafter GUI.

This module is a thin facade that re-exports the public API from focused
sub-modules (see ``_vessel_drafter_scene_*``). Existing imports of
``build_vessel_3d_scene``, ``Vessel3DScene`` and ``VesselSceneMesh`` continue
to work unchanged.
"""

from __future__ import annotations

from functools import lru_cache

from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    VesselDrafterLayout,
)
from programmatic_drafting.preview._vessel_drafter_scene_builders import (
    build_exact_meshes,
    build_fast_meshes,
)
from programmatic_drafting.preview._vessel_drafter_scene_common import (
    DEFAULT_VIEW_OPTIONS,
    Vessel3DScene,
    VesselSceneMesh,
    scene_bounds,
    visible_label_key,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)

__all__ = [
    "Vessel3DScene",
    "VesselSceneMesh",
    "build_vessel_3d_scene",
]


def build_vessel_3d_scene(
    layout: VesselDrafterLayout = DEFAULT_VESSEL_DRAFTER_LAYOUT,
    *,
    visible_labels: set[str] | None = None,
    view_options: Vessel3DViewOptions = DEFAULT_VIEW_OPTIONS,
) -> Vessel3DScene:
    return _build_vessel_3d_scene_cached(
        layout,
        visible_label_key(visible_labels),
        view_options.split_enabled,
        view_options.normalized_split_angle_degrees,
    )


@lru_cache(maxsize=48)
def _build_vessel_3d_scene_cached(
    layout: VesselDrafterLayout,
    visible_label_key_value: tuple[str, ...] | None,
    split_enabled: bool,
    split_angle_degrees: float,
) -> Vessel3DScene:
    view_options = Vessel3DViewOptions(
        split_enabled=split_enabled,
        split_angle_degrees=split_angle_degrees,
    )
    visible_labels = (
        None if visible_label_key_value is None else set(visible_label_key_value)
    )
    if layout.side_ports or layout.lid_ports:
        meshes = build_exact_meshes(layout, visible_labels, view_options)
    else:
        meshes = build_fast_meshes(layout, visible_labels, view_options)
    return Vessel3DScene(meshes=meshes, bounds=scene_bounds(meshes))
