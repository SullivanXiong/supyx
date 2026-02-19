"""
Framework-agnostic keybinding management.

Supports single-key and multi-key sequences (e.g., 'f', 'dd', 'gg').
Delegates scheduling and help display to backend protocols.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from .protocols import HelpDisplay, Scheduler


class KeyBindingEngine:
    """Manages keyboard shortcuts and command mappings.

    Supports multi-key sequences with a timeout buffer.
    Uses Scheduler for deferred execution instead of framework-specific timers.
    """

    def __init__(self, scheduler: Scheduler, help_display: HelpDisplay) -> None:
        self._scheduler = scheduler
        self._help_display = help_display
        self.bindings: dict[str, dict[str, Any]] = {}
        self.multi_key_buffer: list[str] = []
        self._timer_handle: Optional[Any] = None

    def map_key(
        self,
        key_sequence: str,
        callback: Callable[..., Any],
        description: str = "",
    ) -> None:
        """Map a key sequence to a callback function.

        Args:
            key_sequence: String like 'f', 'dd', 'gg', etc.
            callback: Function to call when key sequence is pressed.
            description: Optional description of what the command does.
        """
        self.bindings[key_sequence] = {
            "callback": callback,
            "description": description,
        }

    def unmap_key(self, key_sequence: str) -> None:
        """Remove a key mapping."""
        self.bindings.pop(key_sequence, None)

    def handle_key(self, key: str) -> bool:
        """Handle a key press and check if it matches any bindings.

        Args:
            key: The normalized key string.

        Returns:
            True if the key was handled, False otherwise.
        """
        self.multi_key_buffer.append(key)
        current_sequence = "".join(self.multi_key_buffer)

        # Cancel any pending timeout
        if self._timer_handle is not None:
            self._scheduler.cancel_timer(self._timer_handle)
            self._timer_handle = None

        # Check for exact match
        if current_sequence in self.bindings:
            binding = self.bindings[current_sequence]
            self.multi_key_buffer = []
            self._scheduler.call_soon(binding["callback"])
            return True

        # Check if this could be the start of a longer sequence
        possible_match = any(
            seq.startswith(current_sequence) and len(seq) > len(current_sequence)
            for seq in self.bindings
        )

        if possible_match:
            self._timer_handle = self._scheduler.call_later(
                1000, self._reset_buffer
            )
            return True

        # No match, reset buffer
        self.multi_key_buffer = []
        return False

    def _reset_buffer(self) -> None:
        """Reset the multi-key buffer after timeout."""
        self.multi_key_buffer = []
        self._timer_handle = None

    def get_bindings(self) -> dict[str, dict[str, Any]]:
        """Get all current key bindings."""
        return dict(self.bindings)

    def show_help(self) -> None:
        """Show a help dialog with all key bindings."""
        help_text = "Keyboard Shortcuts:\n\n"
        for key, binding in sorted(self.bindings.items()):
            desc = binding["description"] or "No description"
            help_text += f"{key:10} - {desc}\n"

        self._help_display.show_help(help_text)
