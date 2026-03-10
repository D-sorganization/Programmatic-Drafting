"""STEP-ready geometry for the vessel drafter tool."""

from __future__ import annotations

from math import cos, sin

from build123d import (
    Align,
    Box,
    BuildPart,
    Color,
    Compound,
    Cylinder,
    Locations,
    Mode,
    Plane,
    Solid,
    Sphere,
    add,
)

from programmatic_drafting.models.vessel_drafter import (
    DEFAULT_VESSEL_DRAFTER_LAYOUT,
    MM_PER_INCH,
    RadialBand,
    VesselDrafterLayout,
    VesselElectrodePlacement,
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


def _cap_sphere_radius(base_radius_mm: float, cap_height_mm: float) -> float:
    return ((base_radius_mm**2) + (cap_height_mm**2)) / (2.0 * cap_height_mm)


def _build_spherical_cap(
    base_radius_mm: float,
    cap_height_mm: float,
    springline_z_mm: float,
    upward: bool,
):
    sphere_radius = _cap_sphere_radius(base_radius_mm, cap_height_mm)
    center_z_mm = (
        springline_z_mm + cap_height_mm - sphere_radius
        if upward
        else springline_z_mm - cap_height_mm + sphere_radius
    )
    clip_extent_mm = max(base_radius_mm, cap_height_mm, sphere_radius) * 4.0

    with BuildPart() as spherical_cap:
        with Locations((0.0, 0.0, center_z_mm)):
            Sphere(radius=sphere_radius)
        with Locations((0.0, 0.0, springline_z_mm)):
            Box(
                clip_extent_mm,
                clip_extent_mm,
                clip_extent_mm,
                align=(
                    Align.CENTER,
                    Align.CENTER,
                    Align.MAX if upward else Align.MIN,
                ),
                mode=Mode.SUBTRACT,
            )

    return spherical_cap.part


def _build_head_region(
    inner_base_radius_mm: float | None,
    outer_base_radius_mm: float,
    inner_head_depth_mm: float | None,
    outer_head_depth_mm: float,
    springline_z_mm: float,
    upward: bool,
    label: str,
    color_hex: str,
):
    outer_cap = _build_spherical_cap(
        base_radius_mm=outer_base_radius_mm,
        cap_height_mm=outer_head_depth_mm,
        springline_z_mm=springline_z_mm,
        upward=upward,
    )
    with BuildPart() as head_region:
        add(outer_cap)
        if inner_base_radius_mm is not None and inner_head_depth_mm is not None:
            inner_cap = _build_spherical_cap(
                base_radius_mm=inner_base_radius_mm,
                cap_height_mm=inner_head_depth_mm,
                springline_z_mm=springline_z_mm,
                upward=upward,
            )
            add(inner_cap, mode=Mode.SUBTRACT)

    return _apply_style(head_region.part, label, color_hex)


def _build_sidewall_region(
    band: RadialBand,
    straight_height_mm: float,
):
    with BuildPart() as sidewall_region:
        Cylinder(
            radius=band.outer_radius_in * MM_PER_INCH,
            height=straight_height_mm,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        Cylinder(
            radius=band.inner_radius_in * MM_PER_INCH,
            height=straight_height_mm,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )

    return _apply_style(sidewall_region.part, f"{band.name}_sidewall", band.color_hex)


def _build_glass_bath(layout: VesselDrafterLayout):
    glass_band = layout.radial_bands[0]
    glass = Cylinder(
        radius=glass_band.outer_radius_in * MM_PER_INCH,
        height=layout.glass_height_mm,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    return _apply_style(glass, glass_band.name, glass_band.color_hex)


def _build_top_head_regions(layout: VesselDrafterLayout):
    springline_z_mm = layout.straight_shell_height_mm
    regions = []
    inner_radius_in = layout.inner_radius_in
    inner_head_depth_in = layout.head_depth_in

    for band in layout.shell_bands:
        outer_radius_in = band.outer_radius_in
        outer_head_depth_in = layout.head_depth_for_radius_in(outer_radius_in)
        regions.append(
            _build_head_region(
                inner_base_radius_mm=inner_radius_in * MM_PER_INCH,
                outer_base_radius_mm=outer_radius_in * MM_PER_INCH,
                inner_head_depth_mm=inner_head_depth_in * MM_PER_INCH,
                outer_head_depth_mm=outer_head_depth_in * MM_PER_INCH,
                springline_z_mm=springline_z_mm,
                upward=True,
                label=f"{band.name}_top_head",
                color_hex=band.color_hex,
            )
        )
        inner_radius_in = outer_radius_in
        inner_head_depth_in = outer_head_depth_in

    return regions


def _build_bottom_head_regions(layout: VesselDrafterLayout):
    springline_z_mm = 0.0
    regions = []
    inner_radius_in: float | None = None
    inner_head_depth_in: float | None = None

    for band in layout.shell_bands:
        outer_radius_in = band.outer_radius_in
        outer_head_depth_in = layout.head_depth_for_radius_in(outer_radius_in)
        regions.append(
            _build_head_region(
                inner_base_radius_mm=(
                    None if inner_radius_in is None else inner_radius_in * MM_PER_INCH
                ),
                outer_base_radius_mm=outer_radius_in * MM_PER_INCH,
                inner_head_depth_mm=(
                    None
                    if inner_head_depth_in is None
                    else inner_head_depth_in * MM_PER_INCH
                ),
                outer_head_depth_mm=outer_head_depth_in * MM_PER_INCH,
                springline_z_mm=springline_z_mm,
                upward=False,
                label=f"{band.name}_bottom_head",
                color_hex=band.color_hex,
            )
        )
        inner_radius_in = outer_radius_in
        inner_head_depth_in = outer_head_depth_in

    return regions


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


def build_vessel_drafter_shape(
    layout: VesselDrafterLayout = DEFAULT_VESSEL_DRAFTER_LAYOUT,
) -> Compound:
    children = [_build_glass_bath(layout)]
    children.extend(
        _build_sidewall_region(band, layout.straight_shell_height_mm)
        for band in layout.shell_bands
    )
    children.extend(_build_top_head_regions(layout))
    children.extend(_build_bottom_head_regions(layout))
    children.extend(
        _build_electrode(item, layout) for item in layout.electrode_placements
    )
    return Compound(label="vessel_drafter_default", children=children)
