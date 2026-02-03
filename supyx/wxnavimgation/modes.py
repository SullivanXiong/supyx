"""
Vim-inspired navigation for wxPython applications.

Simplified mode system inspired by Surfingkeys:
- 'i' shows hints on input fields only
- 'f' shows hints on all clickable elements
- '/' enters search mode
- ESC cancels hint/search modes
"""

from enum import Enum

import wx


class VimMode(Enum):
    """Modes for the application."""
    DEFAULT = "DEFAULT"  # Normal state, no overlay active
    HINT = "HINT"        # Hint overlay active
    SEARCH = "SEARCH"    # Search overlay active


class VimNavigationMixin:
    """
    Mixin class to add vim-like navigation to wxPython frames.

    Simplified mode system:
    - Press 'i' to show hints on input fields only
    - Press 'f' to show hints on all clickable elements
    - Press '/' to search
    - Press ESC to cancel hint/search mode

    Usage:
        class MyFrame(VimNavigationMixin, wx.Frame):
            def __init__(self):
                super().__init__(None, title="My App")
                self.init_vim_navigation()
    """

    # Alias for external access
    VimMode = VimMode

    def init_vim_navigation(self):
        """Initialize vim navigation system."""
        from .hints import HintOverlay
        from .keybindings import KeyBindingManager
        from .navigation import NavigationHelper
        from .search import SearchOverlay

        self.vim_mode = VimMode.DEFAULT
        self.vim_bindings = KeyBindingManager(self)
        self.hint_overlay = HintOverlay(self)
        self.search_overlay = SearchOverlay(self)
        self.nav_helper = NavigationHelper(self)

        # Also expose as vim_nav for backward compatibility
        self.vim_nav = self.vim_bindings

        # Bind key events
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        # Optional: create status bar for mode display
        if not self.GetStatusBar():
            self.CreateStatusBar()
        self._update_mode_display()

    def _on_char_hook(self, event):
        """Handle character input."""
        keycode = event.GetKeyCode()

        # Check if we're in an input control
        focused = wx.Window.FindFocus()
        is_input = isinstance(focused, (wx.TextCtrl, wx.ComboBox, wx.SearchCtrl))

        # ESC handling - cancels HINT/SEARCH modes, or removes focus from input
        if keycode == wx.WXK_ESCAPE:
            if self.vim_mode == VimMode.HINT:
                self.hint_overlay.hide()
                self.set_vim_mode(VimMode.DEFAULT)
                return  # Consume the event
            elif self.vim_mode == VimMode.SEARCH:
                self.search_overlay.hide()
                self.set_vim_mode(VimMode.DEFAULT)
                return  # Consume the event
            elif is_input and focused:
                # Remove focus from input field using CallLater for macOS
                def find_focusable(window):
                    """Find a non-input widget that can accept focus."""
                    for child in window.GetChildren():
                        if isinstance(child, wx.ListCtrl):
                            return child
                        result = find_focusable(child)
                        if result:
                            return result
                    return None

                def do_focus():
                    target = find_focusable(self)
                    if target:
                        target.SetFocus()

                # Use CallLater with small delay for macOS compatibility
                wx.CallLater(10, do_focus)
                return  # Consume the event
            else:
                # ESC does nothing in DEFAULT mode without input focus
                event.Skip()
                return

        # In HINT mode, handle hint input
        if self.vim_mode == VimMode.HINT:
            if self.hint_overlay.handle_key(keycode):
                return
            event.Skip()
            return

        # In SEARCH mode, let the search control handle most keys
        if self.vim_mode == VimMode.SEARCH:
            if self.search_overlay.handle_key(keycode):
                return
            event.Skip()
            return

        # In DEFAULT mode with focus on input, let typing happen normally
        if is_input:
            event.Skip()
            return

        # In DEFAULT mode without focus on input, check for navigation keys
        if self.vim_mode == VimMode.DEFAULT:
            key_str = self._get_key_string(event)

            # Built-in navigation keys
            if key_str == 'i':
                self._show_input_hints()
                return
            elif key_str == 'f':
                self._show_all_hints()
                return
            elif key_str == '/':
                self._enter_search_mode()
                return

            # Check custom keybindings
            if self.vim_bindings.handle_key(key_str):
                return

        event.Skip()

    def _get_key_string(self, event):
        """Convert key event to string representation."""
        keycode = event.GetKeyCode()

        # Special keys
        if keycode == wx.WXK_ESCAPE:
            return 'Escape'
        elif keycode == wx.WXK_RETURN:
            return 'Return'
        elif keycode == wx.WXK_TAB:
            return 'Tab'
        elif keycode == wx.WXK_SPACE:
            return 'Space'
        elif keycode == ord('/'):
            return '/'
        elif 32 <= keycode <= 126:  # Printable ASCII
            return chr(keycode).lower()

        return ''

    def set_vim_mode(self, mode):
        """Set the current vim mode."""
        self.vim_mode = mode
        self._update_mode_display()

        # Hide overlays when leaving their modes
        if mode != VimMode.HINT:
            self.hint_overlay.hide()
        if mode != VimMode.SEARCH:
            self.search_overlay.hide()

    def _update_mode_display(self):
        """Update status bar to show current mode (only when in HINT or SEARCH)."""
        if self.GetStatusBar():
            status_bar = self.GetStatusBar()

            # Only show mode indicator for HINT and SEARCH
            if self.vim_mode == VimMode.HINT:
                mode_str = "-- HINTS --"
            elif self.vim_mode == VimMode.SEARCH:
                mode_str = "-- SEARCH --"
            else:
                mode_str = ""

            if status_bar.GetFieldsCount() > 1:
                status_bar.SetStatusText(mode_str, 1)
            else:
                # Add an extra field for mode display
                status_bar.SetFieldsCount(2)
                status_bar.SetStatusWidths([-1, 150])
                status_bar.SetStatusText(mode_str, 1)

    def _show_input_hints(self):
        """Show hints on input fields only (like 'i' in Surfingkeys)."""
        self.set_vim_mode(VimMode.HINT)
        self.hint_overlay.show(hint_type='input')

    def _show_all_hints(self):
        """Show hints on all clickable elements (like 'f' in Surfingkeys)."""
        self.set_vim_mode(VimMode.HINT)
        self.hint_overlay.show(hint_type='all')

    def _enter_search_mode(self):
        """Enter search mode."""
        self.set_vim_mode(VimMode.SEARCH)
        self.search_overlay.show()
