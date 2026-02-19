"""
Backward-compatible VimNavigationMixin for wxPython.

Thin wrapper that creates a WxBackend + ModeStateMachine and
converts wx key events to framework-agnostic KeyEvent objects.
"""

from __future__ import annotations

import wx

from supyx.core.modes import ModeStateMachine
from supyx.core.types import KeyEvent, VimMode

from .backend import WxBackend


class WxVimNavigationMixin:
    """Mixin class to add vim-like navigation to wxPython frames.

    Usage:
        class MyFrame(WxVimNavigationMixin, wx.Frame):
            def __init__(self):
                super().__init__(None, title="My App")
                self.init_vim_navigation()
                self.vim_nav.map_key('dd', self.delete_item, "Delete")
    """

    # Re-export for external access
    VimMode = VimMode

    def init_vim_navigation(self) -> None:
        """Initialize the vim navigation system."""
        self._wx_backend = WxBackend(self)
        self._state_machine = ModeStateMachine(self._wx_backend)

        # Backward-compatible attribute aliases
        self.vim_bindings = self._state_machine.keybinding_engine
        self.vim_nav = self.vim_bindings
        self.hint_overlay = self._state_machine.hint_controller
        self.search_overlay = self._state_machine.search_controller
        self.nav_helper = self._state_machine.navigation_state

        # Bind key events
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        # Create status bar if not present
        if not self.GetStatusBar():
            self.CreateStatusBar()

    @property
    def vim_mode(self) -> VimMode:
        """Current vim mode."""
        return self._state_machine.mode

    def set_vim_mode(self, mode: VimMode) -> None:
        """Set the current vim mode (backward compat)."""
        self._state_machine.set_mode(mode)

    def _on_char_hook(self, event: wx.Event) -> None:
        """Convert wx key event to KeyEvent and dispatch."""
        key_event = self._wx_key_to_key_event(event)
        if self._state_machine.handle_key(key_event):
            return  # Consumed — don't call event.Skip()
        event.Skip()

    @staticmethod
    def _wx_key_to_key_event(event: wx.Event) -> KeyEvent:
        """Convert a wx key event to a framework-agnostic KeyEvent."""
        keycode = event.GetKeyCode()
        key_string = ""

        if keycode == wx.WXK_ESCAPE:
            key_string = "escape"
        elif keycode == wx.WXK_RETURN:
            key_string = "return"
        elif keycode == wx.WXK_TAB:
            key_string = "tab"
        elif keycode == wx.WXK_SPACE:
            key_string = "space"
        elif keycode == ord("/"):
            key_string = "/"
        elif 32 <= keycode <= 126:
            key_string = chr(keycode).lower()

        return KeyEvent(
            key_string=key_string,
            raw_keycode=keycode,
            ctrl=event.ControlDown(),
            alt=event.AltDown(),
            shift=event.ShiftDown(),
        )
