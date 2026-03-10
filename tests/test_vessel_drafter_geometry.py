import pytest

from programmatic_drafting.projects.vessel_drafter_layout import (
    build_vessel_drafter_shape,
)


def test_shape_bounding_box_matches_vessel_envelope() -> None:
    shape = build_vessel_drafter_shape()
    size = shape.bounding_box().size

    assert size.Z == pytest.approx(65.0 * 25.4)
    assert size.X > (74.0 * 25.4)
    assert size.Y > (74.0 * 25.4)
