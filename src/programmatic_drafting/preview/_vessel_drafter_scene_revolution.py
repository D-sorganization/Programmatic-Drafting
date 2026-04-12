"""Revolved-profile mesh generation for the vessel 3D scene."""

from __future__ import annotations

from typing import cast

import numpy as np

from programmatic_drafting.preview._vessel_drafter_scene_common import (
    AXIS_EPSILON_IN,
    FloatArray,
    IntArray,
)
from programmatic_drafting.preview._vessel_drafter_scene_section import (
    preview_angles,
    section_cap_mesh,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)
from programmatic_drafting.projects.vessel_drafter_profiles import ProfilePoint


def revolved_profile_mesh(
    half_profile: tuple[ProfilePoint, ...],
    view_options: Vessel3DViewOptions,
) -> tuple[FloatArray, IntArray]:
    angles = preview_angles(view_options)
    vertices, vertex_groups = _build_revolved_vertices(half_profile, angles)
    face_parts = _build_revolved_faces(vertex_groups, view_options)
    if view_options.split_enabled:
        section_vertices, section_faces = section_cap_mesh(
            half_profile,
            view_options,
        )
        if section_faces.size > 0:
            section_faces = section_faces + len(vertices)
            vertices = np.vstack((vertices, section_vertices))
            face_parts.append(section_faces)
    faces = np.vstack(face_parts)
    return vertices, faces


def _build_revolved_vertices(
    half_profile: tuple[ProfilePoint, ...],
    angles: FloatArray,
) -> tuple[FloatArray, list[int | IntArray]]:
    angle_count = len(angles)
    cos_theta = np.cos(angles)
    sin_theta = np.sin(angles)
    vertex_groups: list[int | IntArray] = []
    vertex_parts: list[FloatArray] = []
    vertex_count = 0

    for point in half_profile:
        if abs(point.x_in) <= AXIS_EPSILON_IN:
            vertex_groups.append(vertex_count)
            vertex_parts.append(np.array([[0.0, 0.0, point.z_in]], dtype=np.float64))
            vertex_count += 1
            continue
        ring = np.column_stack(
            (
                point.x_in * cos_theta,
                point.x_in * sin_theta,
                np.full(angle_count, point.z_in, dtype=np.float64),
            )
        )
        vertex_groups.append(
            np.arange(
                vertex_count,
                vertex_count + angle_count,
                dtype=np.int32,
            )
        )
        vertex_parts.append(ring)
        vertex_count += angle_count

    return np.vstack(vertex_parts), vertex_groups


def _build_revolved_faces(
    vertex_groups: list[int | IntArray],
    view_options: Vessel3DViewOptions,
) -> list[IntArray]:
    face_parts: list[IntArray] = []
    for start_group, end_group in _profile_segments(vertex_groups):
        segment_faces = _segment_faces(
            start_group,
            end_group,
            wrap_around=not view_options.split_enabled,
        )
        if segment_faces.size > 0:
            face_parts.append(segment_faces)
    return face_parts


def _profile_segments(
    vertex_groups: list[int | IntArray],
) -> tuple[tuple[int | IntArray, int | IntArray], ...]:
    return tuple(
        (vertex_groups[index], vertex_groups[(index + 1) % len(vertex_groups)])
        for index in range(len(vertex_groups))
    )


def _segment_faces(
    start_group: int | IntArray,
    end_group: int | IntArray,
    *,
    wrap_around: bool,
) -> IntArray:
    if isinstance(start_group, int) and isinstance(end_group, int):
        return np.empty((0, 3), dtype=np.int32)

    if isinstance(start_group, int):
        ring_indices = _ring_index_pairs(cast(IntArray, end_group), wrap_around)
        return np.column_stack(
            (
                np.full(len(ring_indices), start_group, dtype=np.int32),
                ring_indices[:, 0],
                ring_indices[:, 1],
            )
        )

    if isinstance(end_group, int):
        ring_indices = _ring_index_pairs(cast(IntArray, start_group), wrap_around)
        return np.column_stack(
            (
                np.full(len(ring_indices), end_group, dtype=np.int32),
                ring_indices[:, 1],
                ring_indices[:, 0],
            )
        )

    start_pairs = _ring_index_pairs(start_group, wrap_around)
    end_pairs = _ring_index_pairs(end_group, wrap_around)
    first_faces = np.column_stack(
        (
            start_pairs[:, 0],
            end_pairs[:, 0],
            end_pairs[:, 1],
        )
    )
    second_faces = np.column_stack(
        (
            start_pairs[:, 0],
            end_pairs[:, 1],
            start_pairs[:, 1],
        )
    )
    return np.vstack((first_faces, second_faces))


def _ring_index_pairs(indices: IntArray, wrap_around: bool) -> IntArray:
    if wrap_around:
        return np.column_stack((indices, np.roll(indices, -1)))
    return np.column_stack((indices[:-1], indices[1:]))
