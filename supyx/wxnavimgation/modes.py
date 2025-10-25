"""
Vim mode management for wxPython applications.
"""

from enum import Enum

import wx


class VimMode(Enum):
    """Vim-like modes for the application."""
    NORMAL = "NORMAL"
    INSERT = "INSERT"
    HINT = "HINT"
    SEARCH = "SEARCH"


class VimNavigationMixin:
    """
    Mixin class to add vim-like navigation to wxPython frames.
    
    Usage:
        class MyFrame(VimNavigationMixin, wx.Frame):
            def __init__(self):
                super().__init__(None, title="My App")
                self.init_vim_navigation()
    """
    
    def init_vim_navigation(self):
        """Initialize vim navigation system."""
        from .hints import HintOverlay
        from .keybindings import KeyBindingManager
        from .navigation import NavigationHelper
        from .search import SearchOverlay
        
        self.vim_mode = VimMode.NORMAL
        self.vim_nav = KeyBindingManager(self)
        self.hint_overlay = HintOverlay(self)
        self.search_overlay = SearchOverlay(self)
        self.nav_helper = NavigationHelper(self)
        
        # Bind key events
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.Bind(wx.EVT_SET_FOCUS, self._on_focus_change)
        
        # Setup default keybindings
        self._setup_default_keybindings()
        
        # Create status bar to show mode
        if not self.GetStatusBar():
            self.CreateStatusBar()
        self._update_mode_display()
    
    def _setup_default_keybindings(self):
        """Setup default vim-like keybindings."""
        # Mode switching
        self.vim_nav.map_key('i', self._enter_insert_mode, "Enter insert mode")
        self.vim_nav.map_key('Escape', self._enter_normal_mode, "Enter normal mode")
        
        # Hint mode
        self.vim_nav.map_key('f', self._enter_hint_mode, "Show hints for clickable elements")
        
        # Search mode
        self.vim_nav.map_key('/', self._enter_search_mode, "Search in application")
        
        # Navigation
        self.vim_nav.map_key('gi', self.nav_helper.focus_next_input, "Focus next input field")
    
    def _on_char_hook(self, event):
        """Handle character input."""
        keycode = event.GetKeyCode()
        
        # Check if we're in an input control
        focused = wx.Window.FindFocus()
        is_input = isinstance(focused, (wx.TextCtrl, wx.ComboBox, wx.SearchCtrl))
        
        # In INSERT mode or when focused on input, let event pass through
        if self.vim_mode == VimMode.INSERT or (is_input and self.vim_mode == VimMode.NORMAL):
            event.Skip()
            return
        
        # In HINT mode, handle hint input
        if self.vim_mode == VimMode.HINT:
            if self.hint_overlay.handle_key(keycode):
                return
            event.Skip()
            return
        
        # In SEARCH mode, handle search input
        if self.vim_mode == VimMode.SEARCH:
            if self.search_overlay.handle_key(keycode):
                return
            event.Skip()
            return
        
        # In NORMAL mode, check for keybindings
        if self.vim_mode == VimMode.NORMAL:
            key_str = self._get_key_string(event)
            if self.vim_nav.handle_key(key_str):
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
    
    def _on_focus_change(self, event):
        """Handle focus changes."""
        focused = event.GetWindow()
        is_input = isinstance(focused, (wx.TextCtrl, wx.ComboBox, wx.SearchCtrl))
        
        # Auto-enter insert mode when focusing input
        if is_input and self.vim_mode == VimMode.NORMAL:
            self.set_vim_mode(VimMode.INSERT)
        
        event.Skip()
    
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
        """Update status bar to show current mode."""
        if self.GetStatusBar():
            mode_str = f"-- {self.vim_mode.value} --"
            status_bar = self.GetStatusBar()
            if status_bar.GetFieldsCount() > 1:
                status_bar.SetStatusText(mode_str, 1)
            else:
                # Add an extra field for mode display
                status_bar.SetFieldsCount(2)
                status_bar.SetStatusWidths([-1, 150])
                status_bar.SetStatusText(mode_str, 1)
    
    def _enter_normal_mode(self):
        """Enter normal mode."""
        self.set_vim_mode(VimMode.NORMAL)
    
    def _enter_insert_mode(self):
        """Enter insert mode."""
        self.set_vim_mode(VimMode.INSERT)
        # Focus the first input field
        self.nav_helper.focus_first_input()
    
    def _enter_hint_mode(self):
        """Enter hint mode."""
        self.set_vim_mode(VimMode.HINT)
        self.hint_overlay.show()
    
    def _enter_search_mode(self):
        """Enter search mode."""
        self.set_vim_mode(VimMode.SEARCH)
        self.search_overlay.show()

