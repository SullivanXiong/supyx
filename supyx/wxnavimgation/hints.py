"""
Hint overlay system for clicking elements with keyboard.
"""

import string

import wx


class HintOverlay:
    """
    Displays hints on clickable elements, allowing keyboard-based clicking.
    
    Inspired by Surfingkeys' hint mode.
    """
    
    def __init__(self, parent):
        """
        Initialize the hint overlay.
        
        Args:
            parent: The parent wx.Frame or window
        """
        self.parent = parent
        self.hints = []
        self.hint_windows = []
        self.current_input = ""
        self.hint_chars = string.ascii_lowercase
    
    def show(self):
        """Show hints for all clickable elements."""
        self._clear_hints()
        clickable_widgets = self._find_clickable_widgets()
        
        for i, widget in enumerate(clickable_widgets):
            hint_str = self._generate_hint_string(i)
            self._create_hint_window(widget, hint_str)
            self.hints.append({
                'widget': widget,
                'hint': hint_str
            })
    
    def hide(self):
        """Hide all hint windows."""
        self._clear_hints()
        self.current_input = ""
    
    def handle_key(self, keycode):
        """
        Handle key input in hint mode.
        
        Args:
            keycode: The key code from wx.EVT_CHAR_HOOK
            
        Returns:
            True if the key was handled
        """
        # ESC to cancel
        if keycode == wx.WXK_ESCAPE:
            self.hide()
            self.parent.set_vim_mode(self.parent.vim_mode.__class__.NORMAL)
            return True
        
        # Convert keycode to character
        if 97 <= keycode <= 122:  # a-z
            char = chr(keycode)
        elif 65 <= keycode <= 90:  # A-Z
            char = chr(keycode + 32)  # Convert to lowercase
        else:
            return False
        
        self.current_input += char
        
        # Check for matches
        for hint in self.hints:
            if hint['hint'] == self.current_input:
                # Found a match, click the widget
                self._click_widget(hint['widget'])
                self.hide()
                self.parent.set_vim_mode(self.parent.vim_mode.__class__.NORMAL)
                return True
            elif hint['hint'].startswith(self.current_input):
                # Still a possible match, continue
                pass
        
        return True
    
    def _find_clickable_widgets(self):
        """Find all clickable widgets in the parent window."""
        clickable = []
        
        def traverse(widget):
            if widget.IsShown() and widget.IsEnabled():
                # Check if it's a clickable widget
                if isinstance(widget, (wx.Button, wx.BitmapButton, wx.ToggleButton,
                                     wx.CheckBox, wx.RadioButton, wx.ListCtrl,
                                     wx.Choice, wx.ComboBox)):
                    clickable.append(widget)
                
                # Traverse children
                for child in widget.GetChildren():
                    traverse(child)
        
        traverse(self.parent)
        return clickable
    
    def _generate_hint_string(self, index):
        """
        Generate a hint string for the given index.
        
        Uses single letters for first 26, then two letters for more.
        """
        if index < 26:
            return self.hint_chars[index]
        else:
            first = index // 26 - 1
            second = index % 26
            return self.hint_chars[first] + self.hint_chars[second]
    
    def _create_hint_window(self, widget, hint_str):
        """Create a hint label window on top of the widget."""
        # Get widget position relative to parent
        pos = widget.GetScreenPosition()
        parent_pos = self.parent.GetScreenPosition()
        relative_pos = (pos.x - parent_pos.x, pos.y - parent_pos.y)
        
        # Create a small panel for the hint
        hint_panel = wx.Panel(self.parent, pos=relative_pos, size=(25, 20))
        hint_panel.SetBackgroundColour(wx.Colour(255, 255, 0))  # Yellow background
        
        # Add text
        hint_text = wx.StaticText(hint_panel, label=hint_str, pos=(2, 2))
        font = hint_text.GetFont()
        font.PointSize = 10
        font = font.Bold()
        hint_text.SetFont(font)
        hint_text.SetForegroundColour(wx.Colour(0, 0, 0))  # Black text
        
        self.hint_windows.append(hint_panel)
    
    def _click_widget(self, widget):
        """Simulate a click on the widget."""
        if isinstance(widget, (wx.Button, wx.BitmapButton, wx.ToggleButton)):
            # Generate a button click event
            event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, widget.GetId())
            event.SetEventObject(widget)
            widget.GetEventHandler().ProcessEvent(event)
        elif isinstance(widget, wx.CheckBox):
            widget.SetValue(not widget.GetValue())
            event = wx.CommandEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED, widget.GetId())
            event.SetEventObject(widget)
            widget.GetEventHandler().ProcessEvent(event)
        elif isinstance(widget, wx.ListCtrl):
            widget.SetFocus()
    
    def _clear_hints(self):
        """Clear all hint windows."""
        for window in self.hint_windows:
            window.Destroy()
        self.hint_windows = []
        self.hints = []

