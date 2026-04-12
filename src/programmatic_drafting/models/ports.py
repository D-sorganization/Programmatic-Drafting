"""Shared port geometry helpers for vessel port dataclasses."""

from __future__ import annotations

from math import radians


class PortMixin:
    """Mixin providing shared port geometry properties.

    Inheriting dataclasses must define the following fields:
        clock_angle_degrees: float
        diameter_in: float
    """

    clock_angle_degrees: float
    diameter_in: float

    @property
    def normalized_clock_angle_degrees(self) -> float:
        return self.clock_angle_degrees % 360.0

    @property
    def normalized_clock_angle_radians(self) -> float:
        return radians(self.normalized_clock_angle_degrees)

    @property
    def radius_in(self) -> float:
        return self.diameter_in * 0.5
