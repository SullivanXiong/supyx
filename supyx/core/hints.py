"""
Framework-agnostic hint system.

HintAlgorithm: Pure hint string generation and matching.
HintController: Orchestrates hint mode using backend protocols.

Inspired by Surfingkeys' hint mode.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Sequence

from .protocols import HintRenderer, WidgetActivator, WidgetDiscovery, WidgetInfo
from .types import VimMode

# Left-hand home row priority characters for easier typing.
HINT_CHARACTERS = "asdfgqwertzxcvb"


class HintAlgorithm:
    """Pure hint string generation. No framework imports."""

    @staticmethod
    def generate_hint_string(index: int, chars: str = HINT_CHARACTERS) -> str:
        """Generate a hint string for the given index.

        Uses single characters for the first N elements, then
        two-character combinations, then three-character.

        Args:
            index: The index of the element.
            chars: The character set to use for hints.

        Returns:
            A hint string like 'a', 's', 'd', or 'aa', 'as', etc.
        """
        num_chars = len(chars)

        if index < num_chars:
            return chars[index]

        # Two-character hints
        first_idx = (index - num_chars) // num_chars
        second_idx = (index - num_chars) % num_chars
        if first_idx < num_chars:
            return chars[first_idx] + chars[second_idx]

        # Three-character hints (rare)
        third_idx = first_idx % num_chars
        first_idx = first_idx // num_chars
        return chars[first_idx] + chars[third_idx] + chars[second_idx]


class HintController:
    """Orchestrates hint mode: discovery, rendering, key matching, activation."""

    def __init__(
        self,
        widget_discovery: WidgetDiscovery,
        hint_renderer: HintRenderer,
        widget_activator: WidgetActivator,
        mode_setter: Callable[[VimMode], None],
    ) -> None:
        self._discovery = widget_discovery
        self._renderer = hint_renderer
        self._activator = widget_activator
        self._set_mode = mode_setter
        self._hints: list[dict[str, Any]] = []
        self._hint_handles: list[Any] = []
        self._current_input: str = ""
        self._hint_chars: str = HINT_CHARACTERS

    def show(self, hint_type: str = "all") -> None:
        """Discover widgets, generate hints, display them.

        Args:
            hint_type: "input" for input fields only, "all" for all clickable.
        """
        self.hide()
        widgets: Sequence[WidgetInfo] = self._discovery.find_widgets(hint_type)

        if not widgets:
            self._set_mode(VimMode.DEFAULT)
            return

        for i, widget_info in enumerate(widgets):
            hint_str = HintAlgorithm.generate_hint_string(i, self._hint_chars)
            handle = self._renderer.show_hint(widget_info.handle, hint_str)
            self._hints.append(
                {
                    "widget": widget_info.handle,
                    "widget_type": widget_info.widget_type,
                    "hint": hint_str,
                }
            )
            self._hint_handles.append(handle)

    def hide(self) -> None:
        """Hide all hint labels and reset state."""
        self._renderer.hide_all()
        self._hints = []
        self._hint_handles = []
        self._current_input = ""

    def handle_key(self, keycode: int, char: Optional[str]) -> bool:
        """Handle key input in hint mode.

        Args:
            keycode: Raw keycode (for escape detection — backends pass 27 for ESC).
            char: The lowercase character, or None if not a valid hint char.

        Returns:
            True if the key was consumed.
        """
        # Not a valid hint character — exit hint mode
        if char is None or char not in self._hint_chars:
            self.hide()
            self._set_mode(VimMode.DEFAULT)
            return True  # Consume to prevent accidental typing

        self._current_input += char

        # Filter hints matching current input
        matching = [h for h in self._hints if h["hint"].startswith(self._current_input)]

        # Check for exact match
        for hint in matching:
            if hint["hint"] == self._current_input:
                self._activator.activate(hint["widget"], hint["widget_type"])
                self.hide()
                self._set_mode(VimMode.DEFAULT)
                return True

        # No matches possible — exit
        if not matching:
            self.hide()
            self._set_mode(VimMode.DEFAULT)
            return True

        # Update visual: hide non-matching hints
        for i, hint in enumerate(self._hints):
            if i < len(self._hint_handles):
                visible = hint["hint"].startswith(self._current_input)
                self._renderer.update_visibility(self._hint_handles[i], visible)

        return True
