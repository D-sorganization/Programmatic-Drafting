"""Section cut and triangulation helpers for the vessel 3D scene."""

from __future__ import annotations

from math import pi

import numpy as np

from programmatic_drafting.preview._vessel_drafter_scene_common import (
    DEFAULT_ANGULAR_SEGMENTS,
    FloatArray,
    IntArray,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)
from programmatic_drafting.projects.vessel_drafter_profiles import ProfilePoint


def preview_angles(view_options: Vessel3DViewOptions) -> FloatArray:
    if not view_options.split_enabled:
        return np.linspace(
            0.0,
            2.0 * pi,
            DEFAULT_ANGULAR_SEGMENTS,
            endpoint=False,
            dtype=np.float64,
        )
    return np.linspace(
        view_options.normalized_split_angle_radians,
        view_options.normalized_split_angle_radians + pi,
        (DEFAULT_ANGULAR_SEGMENTS // 2) + 1,
        endpoint=True,
        dtype=np.float64,
    )


def section_cap_mesh(
    half_profile: tuple[ProfilePoint, ...],
    view_options: Vessel3DViewOptions,
) -> tuple[FloatArray, IntArray]:
    triangles = _triangulate_profile_loop(half_profile)
    if not triangles:
        return np.empty((0, 3), dtype=np.float64), np.empty((0, 3), dtype=np.int32)

    start_vertices = _profile_vertices_on_plane(
        half_profile,
        view_options.normalized_split_angle_radians,
    )
    end_vertices = _profile_vertices_on_plane(
        half_profile,
        view_options.normalized_split_angle_radians + pi,
    )
    start_faces = np.array(triangles, dtype=np.int32)
    end_faces = np.array(
        [(third, second, first) for first, second, third in triangles],
        dtype=np.int32,
    ) + len(start_vertices)
    return (
        np.vstack((start_vertices, end_vertices)),
        np.vstack((start_faces, end_faces)),
    )


def _profile_vertices_on_plane(
    half_profile: tuple[ProfilePoint, ...],
    angle_radians: float,
) -> FloatArray:
    direction = np.array(
        [np.cos(angle_radians), np.sin(angle_radians), 0.0],
        dtype=np.float64,
    )
    return np.array(
        [
            (
                point.x_in * direction[0],
                point.x_in * direction[1],
                point.z_in,
            )
            for point in half_profile
        ],
        dtype=np.float64,
    )


def _triangulate_profile_loop(
    half_profile: tuple[ProfilePoint, ...],
) -> tuple[tuple[int, int, int], ...]:
    points = np.array(
        [(point.x_in, point.z_in) for point in half_profile], dtype=np.float64
    )
    indices = list(range(len(points)))
    if len(indices) < 3:
        return ()

    triangles: list[tuple[int, int, int]] = []
    orientation = 1.0 if _signed_area(points) >= 0.0 else -1.0
    guard_limit = len(indices) * len(indices)
    guard_count = 0

    while len(indices) > 3 and guard_count < guard_limit:
        guard_count += 1
        ear_index = _find_ear(points, indices, orientation)
        if ear_index is None:
            break
        triangles.append(ear_index)
        indices.remove(ear_index[1])

    if len(indices) == 3:
        triangles.append((indices[0], indices[1], indices[2]))

    if triangles:
        return tuple(triangles)
    return _fan_triangulation(indices)


def _find_ear(
    points: FloatArray,
    indices: list[int],
    orientation: float,
) -> tuple[int, int, int] | None:
    for position, current in enumerate(indices):
        previous = indices[position - 1]
        following = indices[(position + 1) % len(indices)]
        if not _is_convex(
            points[previous], points[current], points[following], orientation
        ):
            continue
        triangle = np.array(
            [points[previous], points[current], points[following]],
            dtype=np.float64,
        )
        if any(
            _point_in_triangle(points[candidate], triangle)
            for candidate in indices
            if candidate not in (previous, current, following)
        ):
            continue
        return previous, current, following
    return None


def _is_convex(
    previous: FloatArray,
    current: FloatArray,
    following: FloatArray,
    orientation: float,
) -> bool:
    cross_value = _cross_z(previous, current, following)
    return (cross_value * orientation) > 1e-9


def _point_in_triangle(point: FloatArray, triangle: FloatArray) -> bool:
    first_sign = _edge_sign(point, triangle[0], triangle[1])
    second_sign = _edge_sign(point, triangle[1], triangle[2])
    third_sign = _edge_sign(point, triangle[2], triangle[0])
    has_negative = (first_sign < -1e-9) or (second_sign < -1e-9) or (third_sign < -1e-9)
    has_positive = (first_sign > 1e-9) or (second_sign > 1e-9) or (third_sign > 1e-9)
    return not (has_negative and has_positive)


def _edge_sign(point: FloatArray, first: FloatArray, second: FloatArray) -> float:
    return ((point[0] - second[0]) * (first[1] - second[1])) - (
        (first[0] - second[0]) * (point[1] - second[1])
    )


def _cross_z(previous: FloatArray, current: FloatArray, following: FloatArray) -> float:
    first = current - previous
    second = following - current
    return (first[0] * second[1]) - (first[1] * second[0])


def _signed_area(points: FloatArray) -> float:
    shifted = np.roll(points, -1, axis=0)
    cross = (points[:, 0] * shifted[:, 1]) - (shifted[:, 0] * points[:, 1])
    return 0.5 * float(np.sum(cross))


def _fan_triangulation(indices: list[int]) -> tuple[tuple[int, int, int], ...]:
    if len(indices) < 3:
        return ()
    return tuple(
        (indices[0], indices[position], indices[position + 1])
        for position in range(1, len(indices) - 1)
    )


def maybe_apply_section_cut(
    vertices_faces: tuple[FloatArray, IntArray],
    view_options: Vessel3DViewOptions,
) -> tuple[FloatArray, IntArray]:
    if not view_options.split_enabled:
        return vertices_faces
    vertices, faces = vertices_faces
    if faces.size == 0:
        return vertices, faces
    normal = np.array(
        [
            -np.sin(view_options.normalized_split_angle_radians),
            np.cos(view_options.normalized_split_angle_radians),
            0.0,
        ],
        dtype=np.float64,
    )
    centroids = vertices[faces].mean(axis=1)
    mask = (centroids @ normal) >= -1e-9
    return vertices, faces[mask]
