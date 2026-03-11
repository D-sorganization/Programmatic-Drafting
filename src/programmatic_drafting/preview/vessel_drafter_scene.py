"""3D preview scene builders for the vessel drafter GUI."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    MM_PER_INCH,
    VesselDrafterLayout,
)
from programmatic_drafting.projects.vessel_drafter_layout import (
    build_vessel_drafter_components,
)

Point3D = tuple[float, float, float]
Triangle3D = tuple[Point3D, Point3D, Point3D]


@dataclass(frozen=True)
class VesselSceneMesh:
    label: str
    group_label: str
    display_name: str
    color_hex: str
    alpha: float
    triangles: tuple[Triangle3D, ...]


@dataclass(frozen=True)
class Vessel3DScene:
    meshes: tuple[VesselSceneMesh, ...]
    bounds: tuple[float, float, float, float, float, float]


def build_vessel_3d_scene(
    layout: VesselDrafterLayout = DEFAULT_VESSEL_DRAFTER_LAYOUT,
    *,
    visible_labels: set[str] | None = None,
    linear_tolerance_mm: float = 6.0,
) -> Vessel3DScene:
    return _build_vessel_3d_scene_cached(
        layout,
        _visible_label_key(visible_labels),
        linear_tolerance_mm,
    )


@lru_cache(maxsize=48)
def _build_vessel_3d_scene_cached(
    layout: VesselDrafterLayout,
    visible_label_key: tuple[str, ...] | None,
    linear_tolerance_mm: float,
) -> Vessel3DScene:
    visible_labels = None if visible_label_key is None else set(visible_label_key)
    meshes = tuple(
        _mesh_from_component(component, linear_tolerance_mm)
        for component in build_vessel_drafter_components(layout)
        if _is_visible(component.label, component.group_label, visible_labels)
    )
    return Vessel3DScene(meshes=meshes, bounds=_scene_bounds(meshes))


def _mesh_from_component(component, linear_tolerance_mm: float) -> VesselSceneMesh:
    vertices, triangle_indices = component.shape.tessellate(linear_tolerance_mm)
    vertex_points = tuple(_vector_to_inch_point(vertex) for vertex in vertices)
    return VesselSceneMesh(
        label=component.label,
        group_label=component.group_label,
        display_name=component.display_name,
        color_hex=component.color_hex,
        alpha=component.preview_alpha,
        triangles=tuple(
            (
                vertex_points[first_index],
                vertex_points[second_index],
                vertex_points[third_index],
            )
            for first_index, second_index, third_index in triangle_indices
        ),
    )


def _vector_to_inch_point(vector) -> Point3D:
    return (
        vector.X / MM_PER_INCH,
        vector.Y / MM_PER_INCH,
        vector.Z / MM_PER_INCH,
    )


def _is_visible(
    label: str,
    group_label: str,
    visible_labels: set[str] | None,
) -> bool:
    if visible_labels is None:
        return True
    return label in visible_labels or group_label in visible_labels


def _visible_label_key(visible_labels: set[str] | None) -> tuple[str, ...] | None:
    if visible_labels is None:
        return None
    return tuple(sorted(visible_labels))


def _scene_bounds(
    meshes: tuple[VesselSceneMesh, ...],
) -> tuple[float, float, float, float, float, float]:
    points = [
        point for mesh in meshes for triangle in mesh.triangles for point in triangle
    ]
    if not points:
        return (-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]
    z_values = [point[2] for point in points]
    return (
        min(x_values),
        max(x_values),
        min(y_values),
        max(y_values),
        min(z_values),
        max(z_values),
    )
