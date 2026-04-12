"""Shared helpers and types for vessel drafter scene construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

import numpy as np

from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)

FloatArray: TypeAlias = np.ndarray
IntArray: TypeAlias = np.ndarray

AXIS_EPSILON_IN = 1e-6
DEFAULT_ANGULAR_SEGMENTS = 24
DEFAULT_HEAD_SAMPLE_COUNT = 12
DEFAULT_ELECTRODE_SEGMENTS = 12
DEFAULT_VIEW_OPTIONS = Vessel3DViewOptions()


@dataclass(frozen=True)
class VesselSceneMesh:
    label: str
    group_label: str
    display_name: str
    color_hex: str
    alpha: float
    vertices: FloatArray
    faces: IntArray

    @property
    def polygons(self) -> FloatArray:
        return self.vertices[self.faces]


@dataclass(frozen=True)
class Vessel3DScene:
    meshes: tuple[VesselSceneMesh, ...]
    bounds: tuple[float, float, float, float, float, float]


def visible_label_key(visible_labels: set[str] | None) -> tuple[str, ...] | None:
    if visible_labels is None:
        return None
    return tuple(sorted(visible_labels))


def is_visible(
    label: str,
    group_label: str,
    visible_labels: set[str] | None,
) -> bool:
    if visible_labels is None:
        return True
    return label in visible_labels or group_label in visible_labels


def scene_bounds(
    meshes: tuple[VesselSceneMesh, ...],
) -> tuple[float, float, float, float, float, float]:
    vertex_parts = [
        mesh.polygons.reshape(-1, 3) for mesh in meshes if len(mesh.faces) > 0
    ]
    if not vertex_parts:
        return (-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
    all_vertices = np.vstack(vertex_parts)
    return (
        float(np.min(all_vertices[:, 0])),
        float(np.max(all_vertices[:, 0])),
        float(np.min(all_vertices[:, 1])),
        float(np.max(all_vertices[:, 1])),
        float(np.min(all_vertices[:, 2])),
        float(np.max(all_vertices[:, 2])),
    )


def display_alpha(base_alpha: float, view_options: Vessel3DViewOptions) -> float:
    if view_options.split_enabled:
        return 1.0
    return base_alpha


def make_mesh(
    *,
    label: str,
    group_label: str,
    display_name: str,
    color_hex: str,
    alpha: float,
    vertices_faces: tuple[FloatArray, IntArray],
) -> VesselSceneMesh:
    vertices, faces = vertices_faces
    return VesselSceneMesh(
        label=label,
        group_label=group_label,
        display_name=display_name,
        color_hex=color_hex,
        alpha=alpha,
        vertices=vertices,
        faces=faces,
    )
