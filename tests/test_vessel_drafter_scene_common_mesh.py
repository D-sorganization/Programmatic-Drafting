"""Common mesh container and bounds tests for the vessel 3D scene."""

from __future__ import annotations

import numpy as np
import pytest

from programmatic_drafting.preview._vessel_drafter_scene_common import (
    VesselSceneMesh,
    make_mesh,
    scene_bounds,
)


def test_make_mesh_forwards_fields_and_stores_numpy_arrays() -> None:
    vertices = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    faces = np.array([[0, 1, 2]], dtype=np.int32)

    mesh = make_mesh(
        label="label",
        group_label="group",
        display_name="display",
        color_hex="#112233",
        alpha=0.75,
        vertices_faces=(vertices, faces),
    )

    assert isinstance(mesh, VesselSceneMesh)
    assert mesh.label == "label"
    assert mesh.group_label == "group"
    assert mesh.display_name == "display"
    assert mesh.color_hex == "#112233"
    assert mesh.alpha == pytest.approx(0.75)
    assert mesh.vertices is vertices
    assert mesh.faces is faces
    # ``polygons`` property fans out vertices by face indices.
    np.testing.assert_allclose(mesh.polygons, vertices[faces])


def test_scene_bounds_empty_returns_unit_cube_fallback() -> None:
    assert scene_bounds(()) == (-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)


def test_scene_bounds_skips_meshes_with_no_faces() -> None:
    populated_vertices = np.array([[2.0, 3.0, 4.0], [5.0, 6.0, 7.0]])
    populated_faces = np.array([[0, 1, 0]], dtype=np.int32)
    populated = make_mesh(
        label="p",
        group_label="g",
        display_name="d",
        color_hex="#fff",
        alpha=1.0,
        vertices_faces=(populated_vertices, populated_faces),
    )
    empty = make_mesh(
        label="e",
        group_label="g",
        display_name="d",
        color_hex="#000",
        alpha=1.0,
        vertices_faces=(
            np.array([[1000.0, 1000.0, 1000.0]]),
            np.empty((0, 3), dtype=np.int32),
        ),
    )

    bounds = scene_bounds((populated, empty))

    # Empty mesh's vertex must not contaminate bounds.
    assert bounds == (2.0, 5.0, 3.0, 6.0, 4.0, 7.0)


def test_scene_bounds_aggregates_across_multiple_meshes() -> None:
    mesh_a = make_mesh(
        label="a",
        group_label="g",
        display_name="d",
        color_hex="#fff",
        alpha=1.0,
        vertices_faces=(
            np.array([[-1.0, -1.0, -1.0], [0.0, 0.0, 0.0]]),
            np.array([[0, 1, 0]], dtype=np.int32),
        ),
    )
    mesh_b = make_mesh(
        label="b",
        group_label="g",
        display_name="d",
        color_hex="#fff",
        alpha=1.0,
        vertices_faces=(
            np.array([[2.0, 3.0, 4.0], [0.5, 0.5, 0.5]]),
            np.array([[0, 1, 0]], dtype=np.int32),
        ),
    )

    bounds = scene_bounds((mesh_a, mesh_b))

    assert bounds == (-1.0, 2.0, -1.0, 3.0, -1.0, 4.0)
