"""
Textual hint overlay renderer.

Mounts hint labels as Static widgets positioned over target widgets.
"""

from __future__ import annotations

from typing import Any, Optional

from textual.app import App
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import Static


class _HintLabel(Static):
    """A hint label widget styled to overlay a target widget."""

    DEFAULT_CSS = """
    _HintLabel {
        background: #feda31;
        color: #4a400e;
        text-style: bold;
        width: auto;
        height: 1;
        padding: 0 1;
        layer: hints;
    }
    """

    def __init__(self, hint_text: str, hint_id: str) -> None:
        super().__init__(hint_text.upper(), id=hint_id)


class TextualHintRenderer:
    """Renders hint labels as mounted Static overlays in Textual."""

    def __init__(self, app: App) -> None:
        self._app = app
        self._hint_counter = 0
        self._hint_ids: list[str] = []

    def show_hint(self, widget: Any, hint_text: str) -> Any:
        """Mount a hint label. Returns the hint ID string."""
        self._hint_counter += 1
        hint_id = f"hint-{self._hint_counter}"

        hint_label = _HintLabel(hint_text, hint_id)

        # Mount the hint into the app's screen
        self._app.screen.mount(hint_label)
        self._hint_ids.append(hint_id)

        return hint_id

    def hide_hint(self, hint_handle: Any) -> None:
        """Remove a single hint label by ID."""
        if not isinstance(hint_handle, str):
            return
        try:
            widget = self._app.query_one(f"#{hint_handle}", _HintLabel)
            widget.remove()
        except NoMatches:
            pass
        if hint_handle in self._hint_ids:
            self._hint_ids.remove(hint_handle)

    def hide_all(self) -> None:
        """Remove all hint labels."""
        for hint_id in list(self._hint_ids):
            try:
                widget = self._app.query_one(f"#{hint_id}", _HintLabel)
                widget.remove()
            except NoMatches:
                pass
        self._hint_ids.clear()
        self._hint_counter = 0

    def update_visibility(self, hint_handle: Any, visible: bool) -> None:
        """Show or hide a specific hint label."""
        if not isinstance(hint_handle, str):
            return
        try:
            widget = self._app.query_one(f"#{hint_handle}", _HintLabel)
            widget.display = visible
        except NoMatches:
            pass
