"""
Framework-agnostic mode state machine.

Extracted from the wx-specific VimNavigationMixin._on_char_hook.
This is the central key dispatch — it routes key events to the appropriate
handler based on the current vim mode.
"""

from __future__ import annotations

from typing import Callable, Optional

from .clipboard import ClipboardImageDetector
from .editor import EditorLauncher
from .hints import HintController
from .keybindings import KeyBindingEngine
from .navigation import NavigationState
from .protocols import Backend, FocusManager, StatusDisplay
from .search import SearchController
from .types import KeyEvent, VimMode


class ModeStateMachine:
    """Pure state machine for vim mode transitions.

    No framework imports. All UI interaction is via the Backend protocols.
    """

    def __init__(self, backend: Backend) -> None:
        self._backend = backend
        self._mode = VimMode.DEFAULT
        self._status: StatusDisplay = backend.status_display
        self._focus: FocusManager = backend.focus_manager

        # Sub-controllers
        self.keybinding_engine = KeyBindingEngine(
            scheduler=backend.scheduler,
            help_display=backend.help_display,
        )
        self.hint_controller = HintController(
            widget_discovery=backend.widget_discovery,
            hint_renderer=backend.hint_renderer,
            widget_activator=backend.widget_activator,
            mode_setter=self.set_mode,
        )
        self.search_controller = SearchController(
            widget_discovery=backend.widget_discovery,
            search_renderer=backend.search_renderer,
            focus_manager=backend.focus_manager,
            scroll_manager=backend.scroll_manager,
            mode_setter=self.set_mode,
        )
        self.navigation_state = NavigationState(
            widget_discovery=backend.widget_discovery,
            focus_manager=backend.focus_manager,
            scroll_manager=backend.scroll_manager,
        )

        # $EDITOR integration
        self._editor_launcher = EditorLauncher(
            focus_manager=backend.focus_manager,
            widget_discovery=backend.widget_discovery,
            editor_suspender=backend.editor_suspender,
        )

        # Clipboard image detection
        self._clipboard_detector = ClipboardImageDetector()

        # Optional callback for image paste (set by consumer)
        self.on_image_paste: Optional[Callable[[str], None]] = None

    @property
    def mode(self) -> VimMode:
        return self._mode

    def set_mode(self, mode: VimMode) -> None:
        """Transition to a new mode, updating status and hiding overlays."""
        self._mode = mode

        # Hide overlays when leaving their modes
        if mode != VimMode.HINT:
            self.hint_controller.hide()
        if mode != VimMode.SEARCH:
            self.search_controller.hide()

        # Update status display
        status_text = {
            VimMode.HINT: "-- HINTS --",
            VimMode.SEARCH: "-- SEARCH --",
            VimMode.DEFAULT: "",
        }.get(mode, "")
        self._status.set_mode_text(status_text)

    def handle_key(self, key: KeyEvent) -> bool:
        """Central key dispatch. Returns True if the key was consumed.

        This is the framework-agnostic equivalent of _on_char_hook.
        """
        focused = self._focus.get_focused()
        is_input = focused is not None and self._focus.is_input_widget(focused)

        # --- Ctrl+G: open $EDITOR (any mode, when input focused) ---
        if key.ctrl and key.key_string == "g" and is_input:
            if self._editor_launcher is not None:
                self._editor_launcher.launch()
                return True

        # --- Ctrl+V: image paste check (before framework paste) ---
        if key.ctrl and key.key_string == "v":
            if self._clipboard_detector is not None:
                path = self._clipboard_detector.save_image_to_temp()
                if path and self.on_image_paste:
                    self.on_image_paste(path)
                    return True
            # Fall through to let framework handle normal text paste
            return False

        # --- ESC handling ---
        if key.key_string == "escape":
            if self._mode == VimMode.HINT:
                self.hint_controller.hide()
                self.set_mode(VimMode.DEFAULT)
                return True
            elif self._mode == VimMode.SEARCH:
                self.search_controller.hide()
                self.set_mode(VimMode.DEFAULT)
                return True
            elif is_input and focused is not None:
                # Remove focus from input field
                target = self._focus.find_non_input_focusable()
                if target is not None:
                    self._focus.set_focus(target)
                return True
            return False

        # --- HINT mode ---
        if self._mode == VimMode.HINT:
            char = key.key_string if len(key.key_string) == 1 else None
            if self.hint_controller.handle_key(key.raw_keycode, char):
                return True
            return False

        # --- SEARCH mode ---
        if self._mode == VimMode.SEARCH:
            if self.search_controller.handle_key(key):
                return True
            return False

        # --- DEFAULT mode with input focused: let typing happen ---
        if is_input:
            return False

        # --- DEFAULT mode, no input focused: navigation keys ---
        if self._mode == VimMode.DEFAULT:
            if key.key_string == "i":
                self.set_mode(VimMode.HINT)
                self.hint_controller.show(hint_type="input")
                return True
            elif key.key_string == "f":
                self.set_mode(VimMode.HINT)
                self.hint_controller.show(hint_type="all")
                return True
            elif key.key_string == "/":
                self.set_mode(VimMode.SEARCH)
                self.search_controller.show()
                return True

            # Check custom keybindings
            if self.keybinding_engine.handle_key(key.key_string):
                return True

        return False
