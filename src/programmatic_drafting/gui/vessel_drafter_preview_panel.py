"""Reusable zoomable 2D preview panel for the vessel drafter GUI.

The panel wraps a :class:`ZoomableGraphicsView` with a titled header row of
zoom-in / zoom-out / reset buttons. It is intentionally free of vessel-drafter
specific logic so the window can compose one panel per 2D preview (cross-section
and plan view).
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from programmatic_drafting.gui.zoomable_graphics_view import ZoomableGraphicsView


class PreviewPanel(QWidget):
    """Titled zoomable 2D preview panel.

    Parameters
    ----------
    title:
        Human-readable label shown in the header row.
    view:
        The :class:`ZoomableGraphicsView` to host inside the panel. The caller
        remains responsible for attaching a :class:`QGraphicsScene` to the view.
    parent:
        Optional Qt parent widget.
    """

    def __init__(
        self,
        title: str,
        view: ZoomableGraphicsView,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._view = view
        self._title_label = QLabel(title)
        self._zoom_in_button = QPushButton("+")
        self._zoom_in_button.clicked.connect(view.zoom_in)
        self._zoom_out_button = QPushButton("-")
        self._zoom_out_button.clicked.connect(view.zoom_out)
        self._reset_button = QPushButton("Reset")
        self._reset_button.clicked.connect(view.reset_zoom)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self._title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self._zoom_out_button)
        header_layout.addWidget(self._zoom_in_button)
        header_layout.addWidget(self._reset_button)

        panel_layout = QVBoxLayout(self)
        panel_layout.addLayout(header_layout)
        panel_layout.addWidget(view, 1)

    @property
    def view(self) -> ZoomableGraphicsView:
        """Return the hosted zoomable graphics view."""
        return self._view
