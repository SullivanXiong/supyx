"""
Framework-agnostic navigation state.

Tracks input field cycling and delegates scroll/focus to backend protocols.
"""

from __future__ import annotations

from .protocols import FocusManager, ScrollManager, WidgetDiscovery


class NavigationState:
    """Tracks input field cycling index and scroll intent.

    Delegates actual focus and scroll operations to the backend.
    """

    def __init__(
        self,
        widget_discovery: WidgetDiscovery,
        focus_manager: FocusManager,
        scroll_manager: ScrollManager,
    ) -> None:
        self._discovery = widget_discovery
        self._focus = focus_manager
        self._scroll = scroll_manager
        self._current_input_index: int = 0

    def focus_first_input(self) -> None:
        """Focus the first input field."""
        inputs = self._discovery.find_widgets("input")
        if inputs:
            self._focus.set_focus(inputs[0].handle)
            self._current_input_index = 0

    def focus_next_input(self) -> None:
        """Focus the next input field (gi command)."""
        inputs = self._discovery.find_widgets("input")
        if not inputs:
            return
        self._current_input_index = (self._current_input_index + 1) % len(inputs)
        self._focus.set_focus(inputs[self._current_input_index].handle)

    def focus_previous_input(self) -> None:
        """Focus the previous input field."""
        inputs = self._discovery.find_widgets("input")
        if not inputs:
            return
        self._current_input_index = (self._current_input_index - 1) % len(inputs)
        self._focus.set_focus(inputs[self._current_input_index].handle)

    def scroll_up(self) -> None:
        """Scroll focused widget up."""
        focused = self._focus.get_focused()
        if focused:
            self._scroll.scroll_lines(focused, -3)

    def scroll_down(self) -> None:
        """Scroll focused widget down."""
        focused = self._focus.get_focused()
        if focused:
            self._scroll.scroll_lines(focused, 3)

    def go_to_top(self) -> None:
        """Scroll to the top."""
        focused = self._focus.get_focused()
        if focused:
            self._scroll.scroll_to_top(focused)

    def go_to_bottom(self) -> None:
        """Scroll to the bottom."""
        focused = self._focus.get_focused()
        if focused:
            self._scroll.scroll_to_bottom(focused)
