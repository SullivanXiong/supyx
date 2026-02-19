"""
Textual backend VimNavigationMixin.

Thin wrapper that creates a TextualBackend + ModeStateMachine and
converts Textual key events to framework-agnostic KeyEvent objects.

Usage:
    class MyScreen(TextualVimMixin, Screen):
        def on_mount(self) -> None:
            self.init_vim_navigation()
            self.vim_nav.map_key('dd', self.delete_item, "Delete")

Or at the App level:
    class MyApp(TextualVimMixin, App):
        def on_mount(self) -> None:
            self.init_vim_navigation()
"""

from __future__ import annotations

from typing import Callable, Optional

from textual import events
from textual.app import App

from supyx.core.modes import ModeStateMachine
from supyx.core.types import KeyEvent, VimMode

from .backend import TextualBackend


# Map Textual key names to our normalized strings
_KEY_MAP = {
    "escape": "escape",
    "enter": "return",
    "tab": "tab",
    "space": "space",
    "slash": "/",
    "backspace": "backspace",
    "delete": "delete",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "home": "home",
    "end": "end",
    "pageup": "pageup",
    "pagedown": "pagedown",
}


class TextualVimMixin:
    """Mixin class to add vim-like navigation to Textual apps or screens.

    Usage:
        class MyApp(TextualVimMixin, App):
            def on_mount(self) -> None:
                self.init_vim_navigation()
                self.vim_nav.map_key('dd', self.delete_item, "Delete")
    """

    # Re-export for external access
    VimMode = VimMode

    def init_vim_navigation(self) -> None:
        """Initialize the vim navigation system."""
        app = self._get_app()
        self._textual_backend = TextualBackend(app)
        self._state_machine = ModeStateMachine(self._textual_backend)

        # Backward-compatible attribute aliases
        self.vim_bindings = self._state_machine.keybinding_engine
        self.vim_nav = self.vim_bindings
        self.hint_overlay = self._state_machine.hint_controller
        self.search_overlay = self._state_machine.search_controller
        self.nav_helper = self._state_machine.navigation_state

    def _get_app(self) -> App:
        """Get the App instance from self (works for both App and Screen)."""
        if isinstance(self, App):
            return self
        # Screen has .app property
        if hasattr(self, "app"):
            return self.app
        raise RuntimeError("TextualVimMixin must be mixed into an App or Screen")

    @property
    def vim_mode(self) -> VimMode:
        """Current vim mode."""
        return self._state_machine.mode

    def set_vim_mode(self, mode: VimMode) -> None:
        """Set the current vim mode."""
        self._state_machine.set_mode(mode)

    @property
    def on_image_paste(self) -> Optional[Callable[[str], None]]:
        """Get the image paste callback."""
        return self._state_machine.on_image_paste

    @on_image_paste.setter
    def on_image_paste(self, callback: Optional[Callable[[str], None]]) -> None:
        """Set the image paste callback."""
        self._state_machine.on_image_paste = callback

    def vim_handle_key(self, event: events.Key) -> bool:
        """Convert a Textual key event and dispatch through the state machine.

        Call this from on_key() in your App or Screen. Returns True if the
        key was consumed (you should call event.prevent_default() and
        event.stop()).
        """
        key_event = self._textual_key_to_key_event(event)
        return self._state_machine.handle_key(key_event)

    @staticmethod
    def _textual_key_to_key_event(event: events.Key) -> KeyEvent:
        """Convert a Textual Key event to a framework-agnostic KeyEvent."""
        key = event.key
        ctrl = False
        alt = False
        shift = False

        # Parse modifier prefixes from Textual key string
        # Textual uses "ctrl+x", "shift+a", "ctrl+shift+a" format
        parts = key.split("+")
        base_key = parts[-1]

        for part in parts[:-1]:
            if part == "ctrl":
                ctrl = True
            elif part == "alt":
                alt = True
            elif part == "shift":
                shift = True

        # Normalize key string
        key_string = _KEY_MAP.get(base_key, "")
        if not key_string:
            # Single printable character
            if event.character and len(event.character) == 1:
                key_string = event.character.lower()
            elif len(base_key) == 1:
                key_string = base_key.lower()

        return KeyEvent(
            key_string=key_string,
            raw_keycode=ord(key_string) if len(key_string) == 1 else 0,
            ctrl=ctrl,
            alt=alt,
            shift=shift,
        )
