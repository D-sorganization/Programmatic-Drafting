"""Cylinder mesh generation for vessel electrodes in the 3D scene."""

from __future__ import annotations

from math import pi

import numpy as np

from programmatic_drafting.preview._vessel_drafter_scene_common import (
    DEFAULT_ELECTRODE_SEGMENTS,
    FloatArray,
    IntArray,
)


def cylinder_mesh(
    start_point: FloatArray,
    end_point: FloatArray,
    radius_in: float,
) -> tuple[FloatArray, IntArray]:
    radial_unit, binormal_unit = _cylinder_axis_frame(start_point, end_point)
    vertices = _cylinder_vertices(
        start_point,
        end_point,
        radius_in,
        radial_unit,
        binormal_unit,
    )
    faces = _cylinder_faces()
    return vertices, faces


def _cylinder_axis_frame(
    start_point: FloatArray,
    end_point: FloatArray,
) -> tuple[FloatArray, FloatArray]:
    axis_vector = end_point - start_point
    axis_length = np.linalg.norm(axis_vector)
    axis_unit = axis_vector / axis_length
    reference = np.array([0.0, 0.0, 1.0], dtype=np.float64)
    if abs(np.dot(axis_unit, reference)) > 0.95:
        reference = np.array([0.0, 1.0, 0.0], dtype=np.float64)
    radial_unit = np.cross(axis_unit, reference)
    radial_unit /= np.linalg.norm(radial_unit)
    binormal_unit = np.cross(axis_unit, radial_unit)
    return radial_unit, binormal_unit


def _cylinder_vertices(
    start_point: FloatArray,
    end_point: FloatArray,
    radius_in: float,
    radial_unit: FloatArray,
    binormal_unit: FloatArray,
) -> FloatArray:
    angles = np.linspace(
        0.0,
        2.0 * pi,
        DEFAULT_ELECTRODE_SEGMENTS,
        endpoint=False,
        dtype=np.float64,
    )
    ring_offsets = np.column_stack(
        (
            np.cos(angles),
            np.sin(angles),
        )
    )
    radial_offsets = (
        ring_offsets[:, :1] * radial_unit[np.newaxis, :]
        + ring_offsets[:, 1:] * binormal_unit[np.newaxis, :]
    ) * radius_in
    start_ring = start_point[np.newaxis, :] + radial_offsets
    end_ring = end_point[np.newaxis, :] + radial_offsets
    return np.vstack((start_ring, end_ring, start_point, end_point))


def _cylinder_faces() -> IntArray:
    lower_indices = np.arange(DEFAULT_ELECTRODE_SEGMENTS, dtype=np.int32)
    upper_indices = lower_indices + DEFAULT_ELECTRODE_SEGMENTS
    start_center_index = np.int32(DEFAULT_ELECTRODE_SEGMENTS * 2)
    end_center_index = np.int32(start_center_index + 1)
    side_faces = np.vstack(
        (
            np.column_stack((lower_indices, upper_indices, np.roll(upper_indices, -1))),
            np.column_stack(
                (
                    lower_indices,
                    np.roll(upper_indices, -1),
                    np.roll(lower_indices, -1),
                )
            ),
        )
    )
    start_cap = np.column_stack(
        (
            np.full(DEFAULT_ELECTRODE_SEGMENTS, start_center_index, dtype=np.int32),
            np.roll(lower_indices, -1),
            lower_indices,
        )
    )
    end_cap = np.column_stack(
        (
            np.full(DEFAULT_ELECTRODE_SEGMENTS, end_center_index, dtype=np.int32),
            upper_indices,
            np.roll(upper_indices, -1),
        )
    )
    return np.vstack((side_faces, start_cap, end_cap))
