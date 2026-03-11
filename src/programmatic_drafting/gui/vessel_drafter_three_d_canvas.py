"""Matplotlib-backed 3D canvas for vessel drafter previews."""

from __future__ import annotations

from typing import Any

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from programmatic_drafting.preview.vessel_drafter_scene import Vessel3DScene

DEFAULT_VIEW = (25.0, -55.0)


class VesselDrafterThreeDCanvas(FigureCanvasQTAgg):
    def __init__(self) -> None:
        self.figure = Figure(figsize=(7.5, 6.0))
        super().__init__(self.figure)
        self._scene: Vessel3DScene | None = None
        self._view_state = DEFAULT_VIEW
        self.current_labels: tuple[str, ...] = ()
        self.current_face_count = 0

    def draw_scene(self, scene: Vessel3DScene) -> None:
        self._capture_view_state()
        self._scene = scene
        self.current_labels = tuple(mesh.label for mesh in scene.meshes)
        self.current_face_count = sum(len(mesh.faces) for mesh in scene.meshes)
        self.figure.clear()
        axes = self.figure.add_subplot(111, projection="3d")
        for mesh in scene.meshes:
            axes.add_collection3d(
                Poly3DCollection(
                    mesh.polygons,
                    facecolors=mesh.color_hex,
                    edgecolors="none",
                    linewidths=0.0,
                    alpha=mesh.alpha,
                )
            )
        self._apply_axes_formatting(axes, scene)
        self.draw_idle()

    def reset_view(self) -> None:
        self._view_state = DEFAULT_VIEW
        if self._scene is not None:
            self.draw_scene(self._scene)

    def _capture_view_state(self) -> None:
        if not self.figure.axes:
            return
        axes: Any = self.figure.axes[0]
        self._view_state = (axes.elev, axes.azim)

    def _apply_axes_formatting(self, axes: Any, scene: Vessel3DScene) -> None:
        min_x, max_x, min_y, max_y, min_z, max_z = scene.bounds
        span_x = max(max_x - min_x, 1.0)
        span_y = max(max_y - min_y, 1.0)
        span_z = max(max_z - min_z, 1.0)
        axes.set_xlim(*_expand_limits(min_x, max_x, span_x))
        axes.set_ylim(*_expand_limits(min_y, max_y, span_y))
        axes.set_zlim(*_expand_limits(min_z, max_z, span_z))
        axes.set_box_aspect((span_x, span_y, span_z))
        axes.set_axis_off()
        axes.view_init(elev=self._view_state[0], azim=self._view_state[1])


def _expand_limits(minimum: float, maximum: float, span: float) -> tuple[float, float]:
    padding = span * 0.12
    return minimum - padding, maximum + padding
