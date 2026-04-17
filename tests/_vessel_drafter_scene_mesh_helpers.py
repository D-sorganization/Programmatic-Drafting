"""Shared helpers for vessel scene mesh tests."""

from __future__ import annotations

import numpy as np

from programmatic_drafting.projects.vessel_drafter_profiles import ProfilePoint


def triangle_mesh_surface_area(vertices: np.ndarray, faces: np.ndarray) -> float:
    """Sum of absolute triangle areas for a triangle-face mesh."""
    triangles = vertices[faces]
    edge_a = triangles[:, 1] - triangles[:, 0]
    edge_b = triangles[:, 2] - triangles[:, 0]
    cross = np.cross(edge_a, edge_b)
    return float(0.5 * np.linalg.norm(cross, axis=1).sum())


def rectangle_profile() -> tuple[ProfilePoint, ...]:
    """Rectangular profile that revolves into a disc of radius 1, height 2."""
    return (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(1.0, 0.0),
        ProfilePoint(1.0, 2.0),
        ProfilePoint(0.0, 2.0),
    )
