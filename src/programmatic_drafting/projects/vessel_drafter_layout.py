"""STEP-ready geometry for the vessel drafter tool."""

from __future__ import annotations

from math import cos, sin

from build123d import (
    Axis,
    BuildLine,
    BuildSketch,
    Color,
    Compound,
    Plane,
    Polyline,
    Solid,
    make_face,
    revolve,
)

from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    MM_PER_INCH,
    VesselDrafterLayout,
    VesselElectrodePlacement,
    VesselLidPort,
    VesselSidePort,
)
from programmatic_drafting.projects.vessel_drafter_profiles import (
    ProfilePoint,
    build_cavity_boundary_half,
    build_glass_boundary_half,
    build_shell_band_profiles,
    build_shell_boundary_half,
)


def _color_from_hex(color_hex: str) -> Color:
    red = int(color_hex[1:3], 16) / 255.0
    green = int(color_hex[3:5], 16) / 255.0
    blue = int(color_hex[5:7], 16) / 255.0
    return Color(red, green, blue)


def _apply_style(shape, label: str, color_hex: str):
    shape.label = label
    shape.color = _color_from_hex(color_hex)
    return shape


def _points_to_mm(points: tuple[ProfilePoint, ...]) -> list[tuple[float, float]]:
    return [(point.x_in * MM_PER_INCH, point.z_in * MM_PER_INCH) for point in points]


def _build_revolved_profile(
    half_profile: tuple[ProfilePoint, ...],
    label: str,
    color_hex: str,
):
    with BuildSketch(Plane.XZ) as sketch:
        with BuildLine():
            Polyline(_points_to_mm(half_profile), close=True)
        make_face()
    part = revolve(sketch.sketch.face(), axis=Axis.Z)
    return _apply_style(part, label, color_hex)


def _build_glass_bath(layout: VesselDrafterLayout):
    return _build_revolved_profile(
        build_glass_boundary_half(layout),
        label="glass_bath",
        color_hex=layout.layers[0].color_hex,
    )


def _build_shell_band_shapes(layout: VesselDrafterLayout):
    shapes = []
    for profile in build_shell_band_profiles(layout):
        inner_half = (
            build_cavity_boundary_half(layout)
            if profile.inner_offset_in == 0.0
            else build_shell_boundary_half(layout, profile.inner_offset_in)
        )
        outer_half = build_shell_boundary_half(layout, profile.outer_offset_in)
        shapes.append(
            _build_revolved_profile(
                outer_half + tuple(reversed(inner_half)),
                label=profile.band.label,
                color_hex=profile.band.color_hex,
            )
        )
    return shapes


def _build_electrode(
    placement: VesselElectrodePlacement,
    layout: VesselDrafterLayout,
):
    direction_x = cos(placement.angle_radians)
    direction_y = sin(placement.angle_radians)
    inner_tip_x_mm = placement.inner_tip_radius_in * direction_x * MM_PER_INCH
    inner_tip_y_mm = placement.inner_tip_radius_in * direction_y * MM_PER_INCH
    outer_tip_x_mm = placement.outer_tip_radius_in * direction_x * MM_PER_INCH
    outer_tip_y_mm = placement.outer_tip_radius_in * direction_y * MM_PER_INCH
    plane = Plane(
        origin=(
            inner_tip_x_mm,
            inner_tip_y_mm,
            layout.electrode_centerline_height_mm,
        ),
        x_dir=(0.0, 0.0, 1.0),
        z_dir=(
            outer_tip_x_mm - inner_tip_x_mm,
            outer_tip_y_mm - inner_tip_y_mm,
            0.0,
        ),
    )
    electrode = Solid.make_cylinder(
        radius=layout.electrode_radius_mm,
        height=layout.electrode_length_mm,
        plane=plane,
    )
    return _apply_style(electrode, f"electrode_{placement.index}", "#2B2B2B")


def _build_side_port_cutter(
    port: VesselSidePort,
    layout: VesselDrafterLayout,
):
    direction_x = cos(port.normalized_clock_angle_radians)
    direction_y = sin(port.normalized_clock_angle_radians)
    start_radius_in = layout.inner_radius_in - 1.0
    cutter_length_in = layout.total_shell_thickness_in + 2.0
    plane = Plane(
        origin=(
            direction_x * start_radius_in * MM_PER_INCH,
            direction_y * start_radius_in * MM_PER_INCH,
            port.centerline_height_in(layout) * MM_PER_INCH,
        ),
        x_dir=(0.0, 0.0, 1.0),
        z_dir=(direction_x, direction_y, 0.0),
    )
    return Solid.make_cylinder(
        radius=port.radius_in * MM_PER_INCH,
        height=cutter_length_in * MM_PER_INCH,
        plane=plane,
    )


def _build_lid_port_cutter(
    port: VesselLidPort,
    layout: VesselDrafterLayout,
):
    direction_x = cos(port.normalized_clock_angle_radians)
    direction_y = sin(port.normalized_clock_angle_radians)
    start_z_in = layout.glass_depth_in
    cutter_height_in = layout.plenum_height_in + layout.outer_head_depth_in + 1.0
    plane = Plane(
        origin=(
            direction_x * port.radial_distance_from_center_in * MM_PER_INCH,
            direction_y * port.radial_distance_from_center_in * MM_PER_INCH,
            start_z_in * MM_PER_INCH,
        ),
        x_dir=(1.0, 0.0, 0.0),
        z_dir=(0.0, 0.0, 1.0),
    )
    return Solid.make_cylinder(
        radius=port.radius_in * MM_PER_INCH,
        height=cutter_height_in * MM_PER_INCH,
        plane=plane,
    )


def _port_cutters(layout: VesselDrafterLayout) -> tuple[Solid, ...]:
    side_cutters = tuple(
        _build_side_port_cutter(port, layout) for port in layout.side_ports
    )
    lid_cutters = tuple(
        _build_lid_port_cutter(port, layout) for port in layout.lid_ports
    )
    return side_cutters + lid_cutters


def _cut_ports(shape, cutters: tuple[Solid, ...]):
    if not cutters:
        return shape
    return shape.cut(*cutters)


def build_vessel_drafter_shape(
    layout: VesselDrafterLayout = DEFAULT_VESSEL_DRAFTER_LAYOUT,
) -> Compound:
    cutters = _port_cutters(layout)
    children = [
        _apply_style(
            _cut_ports(_build_glass_bath(layout), cutters),
            "glass_bath",
            layout.layers[0].color_hex,
        ),
        *(
            _apply_style(_cut_ports(shape, cutters), band.label, band.color_hex)
            for shape, band in zip(
                _build_shell_band_shapes(layout),
                layout.shell_bands,
                strict=True,
            )
        ),
    ]
    children.extend(
        _build_electrode(item, layout) for item in layout.electrode_placements
    )
    return Compound(label="vessel_drafter_default", children=children)
