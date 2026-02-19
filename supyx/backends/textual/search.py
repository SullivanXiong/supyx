"""
Textual search bar renderer.

Creates a search bar at the bottom of the screen using Input widget.
"""

from __future__ import annotations

from typing import Callable, Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import Input, Static


class _SearchBar(Horizontal):
    """Search bar widget with prompt, input, and info label."""

    DEFAULT_CSS = """
    _SearchBar {
        dock: bottom;
        height: 1;
        background: #323232;
        padding: 0;
    }

    _SearchBar #search-prompt {
        width: 2;
        color: white;
        background: #323232;
    }

    _SearchBar #search-input {
        width: 1fr;
        border: none;
        background: #323232;
        color: white;
    }

    _SearchBar #search-input:focus {
        border: none;
    }

    _SearchBar #search-info {
        width: auto;
        min-width: 12;
        color: #c8c8c8;
        background: #323232;
        padding: 0 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._on_text_changed: Optional[Callable[[str], None]] = None

    def compose(self) -> ComposeResult:
        yield Static("/", id="search-prompt")
        yield Input(placeholder="Search...", id="search-input")
        yield Static("0 matches", id="search-info")

    def on_input_changed(self, event: Input.Changed) -> None:
        if self._on_text_changed:
            self._on_text_changed(event.value)


class TextualSearchRenderer:
    """Renders the search bar as a mounted widget in Textual."""

    def __init__(self, app: App) -> None:
        self._app = app
        self._search_bar: Optional[_SearchBar] = None

    def show(self) -> None:
        """Show the search bar."""
        if self._search_bar is not None:
            self._search_bar.display = True
            self.focus_search_input()
            return

        self._search_bar = _SearchBar()
        self._app.screen.mount(self._search_bar)
        # Defer focus to after mount completes
        self._app.call_later(self.focus_search_input)

    def hide(self) -> None:
        """Hide the search bar."""
        if self._search_bar is not None:
            self._search_bar.display = False

    def get_query(self) -> str:
        """Get the current search query text."""
        if self._search_bar is None:
            return ""
        try:
            input_widget = self._search_bar.query_one("#search-input", Input)
            return input_widget.value
        except NoMatches:
            return ""

    def set_info_text(self, text: str) -> None:
        """Update the match count/info label."""
        if self._search_bar is None:
            return
        try:
            info = self._search_bar.query_one("#search-info", Static)
            info.update(text)
        except NoMatches:
            pass

    def focus_search_input(self) -> None:
        """Focus the search text input."""
        if self._search_bar is None:
            return
        try:
            input_widget = self._search_bar.query_one("#search-input", Input)
            input_widget.focus()
        except NoMatches:
            pass

    def set_on_text_changed(self, callback: Callable[[str], None]) -> None:
        """Register a callback for live search text changes."""
        if self._search_bar is not None:
            self._search_bar._on_text_changed = callback
        # Also store for deferred setup
        self._on_text_changed_cb = callback

    def _ensure_callback(self) -> None:
        """Ensure the callback is wired after mount."""
        if self._search_bar and hasattr(self, "_on_text_changed_cb"):
            self._search_bar._on_text_changed = self._on_text_changed_cb
