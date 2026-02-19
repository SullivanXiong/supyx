"""
Framework-agnostic search system.

SearchEngine: Pure search matching logic.
SearchController: Orchestrates search mode using backend protocols.
"""

from __future__ import annotations

from typing import Callable, Sequence

from .protocols import (
    FocusManager,
    ScrollManager,
    SearchRenderer,
    WidgetDiscovery,
    WidgetInfo,
)
from .types import KeyEvent, VimMode


class SearchEngine:
    """Pure search matching logic. No framework imports."""

    @staticmethod
    def find_matches(query: str, items: Sequence[WidgetInfo]) -> list[WidgetInfo]:
        """Case-insensitive substring search across widget text.

        Args:
            query: Search query string.
            items: Widgets to search through.

        Returns:
            List of matching WidgetInfo objects.
        """
        query_lower = query.lower()
        return [item for item in items if query_lower in item.text.lower()]


class SearchController:
    """Orchestrates search mode: rendering, matching, navigation."""

    def __init__(
        self,
        widget_discovery: WidgetDiscovery,
        search_renderer: SearchRenderer,
        focus_manager: FocusManager,
        scroll_manager: ScrollManager,
        mode_setter: Callable[[VimMode], None],
    ) -> None:
        self._discovery = widget_discovery
        self._renderer = search_renderer
        self._focus = focus_manager
        self._scroll = scroll_manager
        self._set_mode = mode_setter
        self._matches: list[WidgetInfo] = []
        self._current_match_index: int = 0

        # Wire up live search callback
        self._renderer.set_on_text_changed(self._on_query_changed)

    def show(self) -> None:
        """Show the search bar and enter search mode."""
        self._renderer.show()
        self._renderer.focus_search_input()

    def hide(self) -> None:
        """Hide the search bar and clear matches."""
        self._renderer.hide()
        self._matches = []
        self._current_match_index = 0

    def handle_key(self, key: KeyEvent) -> bool:
        """Handle key input in search mode.

        Returns:
            True if the key was consumed.
        """
        if key.key_string == "escape":
            self.hide()
            self._set_mode(VimMode.DEFAULT)
            return True

        if key.key_string == "return":
            self._search_next()
            return True

        # Let the search input handle other keys
        return False

    def search(self, query: str) -> None:
        """Search for text across all widgets."""
        all_widgets = self._discovery.find_widgets("all")
        self._matches = SearchEngine.find_matches(query, all_widgets)

        count = len(self._matches)
        self._renderer.set_info_text(
            f"{count} match{'es' if count != 1 else ''}"
        )

        if self._matches:
            self._current_match_index = 0
            self._highlight_current()

    def _search_next(self) -> None:
        """Move to the next match."""
        if not self._matches:
            return
        self._current_match_index = (
            (self._current_match_index + 1) % len(self._matches)
        )
        self._highlight_current()

    def _highlight_current(self) -> None:
        """Focus and scroll to the current match."""
        if not self._matches:
            return
        match = self._matches[self._current_match_index]
        self._focus.set_focus(match.handle)
        self._scroll.ensure_visible(match.handle)
        self._renderer.set_info_text(
            f"{self._current_match_index + 1}/{len(self._matches)}"
        )

    def _on_query_changed(self, query: str) -> None:
        """Handle live search text changes."""
        if query:
            self.search(query)
        else:
            self._matches = []
            self._current_match_index = 0
            self._renderer.set_info_text("0 matches")
