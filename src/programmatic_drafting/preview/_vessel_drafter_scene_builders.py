"""Component mesh builders for the vessel 3D preview scene."""

from __future__ import annotations

import numpy as np

from programmatic_drafting.constants import MM_PER_INCH
from programmatic_drafting.models.vessel_drafter import VesselDrafterLayout
from programmatic_drafting.preview._vessel_drafter_scene_common import (
    DEFAULT_HEAD_SAMPLE_COUNT,
    FloatArray,
    IntArray,
    VesselSceneMesh,
    display_alpha,
    is_visible,
    make_mesh,
)
from programmatic_drafting.preview._vessel_drafter_scene_cylinder import cylinder_mesh
from programmatic_drafting.preview._vessel_drafter_scene_revolution import (
    revolved_profile_mesh,
)
from programmatic_drafting.preview._vessel_drafter_scene_section import (
    maybe_apply_section_cut,
)
from programmatic_drafting.preview.vessel_drafter_view_options import (
    Vessel3DViewOptions,
)
from programmatic_drafting.projects.vessel_drafter_layout import (
    build_vessel_drafter_components,
)
from programmatic_drafting.projects.vessel_drafter_profiles import (
    ProfilePoint,
    build_bottom_head_curve,
    build_glass_boundary_half,
    build_shell_band_profiles,
    build_top_head_curve,
)


def build_fast_meshes(
    layout: VesselDrafterLayout,
    visible_labels: set[str] | None,
    view_options: Vessel3DViewOptions,
) -> tuple[VesselSceneMesh, ...]:
    meshes = [
        _build_glass_mesh(layout, visible_labels, view_options),
        *_build_shell_meshes(layout, visible_labels, view_options),
        *_build_electrode_meshes(layout, visible_labels, view_options),
    ]
    return tuple(mesh for mesh in meshes if mesh is not None)


def build_exact_meshes(
    layout: VesselDrafterLayout,
    visible_labels: set[str] | None,
    view_options: Vessel3DViewOptions,
) -> tuple[VesselSceneMesh, ...]:
    meshes: list[VesselSceneMesh] = []
    for component in build_vessel_drafter_components(layout):
        if not is_visible(component.label, component.group_label, visible_labels):
            continue
        vertices_faces = maybe_apply_section_cut(
            _exact_component_mesh(component),
            view_options,
        )
        if vertices_faces[1].size == 0:
            continue
        meshes.append(
            make_mesh(
                label=component.label,
                group_label=component.group_label,
                display_name=component.display_name,
                color_hex=component.color_hex,
                alpha=display_alpha(component.preview_alpha, view_options),
                vertices_faces=vertices_faces,
            )
        )
    return tuple(meshes)


def _build_glass_mesh(
    layout: VesselDrafterLayout,
    visible_labels: set[str] | None,
    view_options: Vessel3DViewOptions,
) -> VesselSceneMesh | None:
    layer = layout.layers[0]
    if not is_visible(layer.name, layer.name, visible_labels):
        return None
    return make_mesh(
        label=layer.name,
        group_label=layer.name,
        display_name=layer.display_name,
        color_hex=layer.color_hex,
        alpha=display_alpha(layer.preview_alpha, view_options),
        vertices_faces=revolved_profile_mesh(
            build_glass_boundary_half(layout),
            view_options,
        ),
    )


def _build_shell_meshes(
    layout: VesselDrafterLayout,
    visible_labels: set[str] | None,
    view_options: Vessel3DViewOptions,
) -> tuple[VesselSceneMesh, ...]:
    meshes: list[VesselSceneMesh] = []
    for profile in build_shell_band_profiles(layout):
        band = profile.band
        if not is_visible(band.label, band.label, visible_labels):
            continue
        inner_half = (
            _build_cavity_boundary_half(layout)
            if profile.inner_offset_in == 0.0
            else _build_shell_boundary_half(layout, profile.inner_offset_in)
        )
        outer_half = _build_shell_boundary_half(layout, profile.outer_offset_in)
        meshes.append(
            make_mesh(
                label=band.label,
                group_label=band.label,
                display_name=layout.material_properties_by_name[
                    band.label
                ].display_name,
                color_hex=band.color_hex,
                alpha=display_alpha(
                    layout.material_properties_by_name[band.label].preview_alpha,
                    view_options,
                ),
                vertices_faces=revolved_profile_mesh(
                    outer_half + tuple(reversed(inner_half)),
                    view_options,
                ),
            )
        )
    return tuple(meshes)


def _build_electrode_meshes(
    layout: VesselDrafterLayout,
    visible_labels: set[str] | None,
    view_options: Vessel3DViewOptions,
) -> tuple[VesselSceneMesh, ...]:
    if not is_visible("electrodes", "electrodes", visible_labels):
        return ()
    meshes: list[VesselSceneMesh] = []
    material = layout.material_properties_by_name["electrodes"]
    for placement in layout.electrode_placements:
        label = f"electrode_{placement.index}"
        if not is_visible(label, "electrodes", visible_labels):
            continue
        start_point = np.array(
            [
                placement.inner_tip_radius_in * np.cos(placement.angle_radians),
                placement.inner_tip_radius_in * np.sin(placement.angle_radians),
                layout.electrode_centerline_height_in,
            ],
            dtype=np.float64,
        )
        end_point = np.array(
            [
                placement.outer_tip_radius_in * np.cos(placement.angle_radians),
                placement.outer_tip_radius_in * np.sin(placement.angle_radians),
                layout.electrode_centerline_height_in,
            ],
            dtype=np.float64,
        )
        vertices_faces = maybe_apply_section_cut(
            cylinder_mesh(
                start_point,
                end_point,
                layout.electrode_radius_in,
            ),
            view_options,
        )
        if vertices_faces[1].size == 0:
            continue
        meshes.append(
            make_mesh(
                label=label,
                group_label="electrodes",
                display_name=material.display_name,
                color_hex=material.color_hex,
                alpha=display_alpha(material.preview_alpha, view_options),
                vertices_faces=vertices_faces,
            )
        )
    return tuple(meshes)


def _exact_component_mesh(component) -> tuple[FloatArray, IntArray]:
    vertices, triangle_indices = component.shape.tessellate(6.0)
    vertex_array = np.array(
        [_vector_to_inch_point(vertex) for vertex in vertices],
        dtype=np.float64,
    )
    face_array = np.array(triangle_indices, dtype=np.int32)
    return vertex_array, face_array


def _vector_to_inch_point(vector) -> tuple[float, float, float]:
    return (
        vector.X / MM_PER_INCH,
        vector.Y / MM_PER_INCH,
        vector.Z / MM_PER_INCH,
    )


def _build_cavity_boundary_half(
    layout: VesselDrafterLayout,
) -> tuple[ProfilePoint, ...]:
    return (
        ProfilePoint(0.0, 0.0),
        ProfilePoint(layout.inner_radius_in, 0.0),
        ProfilePoint(layout.inner_radius_in, layout.straight_shell_height_in),
        *build_top_head_curve(
            layout,
            0.0,
            sample_count=DEFAULT_HEAD_SAMPLE_COUNT,
        )[1:],
    )


def _build_shell_boundary_half(
    layout: VesselDrafterLayout,
    offset_in: float,
) -> tuple[ProfilePoint, ...]:
    radius_in = layout.inner_radius_in + offset_in
    return (
        *build_bottom_head_curve(
            layout,
            offset_in,
            sample_count=DEFAULT_HEAD_SAMPLE_COUNT,
        ),
        ProfilePoint(radius_in, layout.straight_shell_height_in),
        *build_top_head_curve(
            layout,
            offset_in,
            sample_count=DEFAULT_HEAD_SAMPLE_COUNT,
        )[1:],
    )
