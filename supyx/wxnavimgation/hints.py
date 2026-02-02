"""
Hint overlay system for clicking elements with keyboard.

Inspired by Surfingkeys' hint mode:
- 'i' shows hints on input fields only
- 'f' shows hints on all clickable elements
- Hint characters: asdfgqwertzxcvb (left-hand home row priority)
"""

import wx


# Left-hand home row priority characters for easier typing
HINT_CHARACTERS = "asdfgqwertzxcvb"


class HintOverlay:
    """
    Displays hints on elements, allowing keyboard-based interaction.

    Supports two hint types:
    - 'input': Only shows hints on input fields (TextCtrl, ComboBox, SearchCtrl)
    - 'all': Shows hints on all clickable elements (buttons, checkboxes, etc.)

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
        self.hint_chars = HINT_CHARACTERS

    def show(self, hint_type="all"):
        """
        Show hints for elements.

        Args:
            hint_type: 'input' for input fields only, 'all' for all clickable elements
        """
        self._clear_hints()
        widgets = self._find_widgets(hint_type)

        if not widgets:
            # No widgets found, exit hint mode
            from .modes import VimMode
            self.parent.set_vim_mode(VimMode.DEFAULT)
            return

        for i, widget in enumerate(widgets):
            hint_str = self._generate_hint_string(i)
            self._create_hint_window(widget, hint_str)
            self.hints.append({
                "widget": widget,
                "hint": hint_str
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
        # ESC is handled by modes.py now, but keep for safety
        if keycode == wx.WXK_ESCAPE:
            self.hide()
            from .modes import VimMode
            self.parent.set_vim_mode(VimMode.DEFAULT)
            return True

        # Convert keycode to character
        char = None
        if 97 <= keycode <= 122:  # a-z
            char = chr(keycode)
        elif 65 <= keycode <= 90:  # A-Z
            char = chr(keycode + 32)  # Convert to lowercase

        # If not a valid hint character, exit hint mode
        if char is None or char not in self.hint_chars:
            self.hide()
            from .modes import VimMode
            self.parent.set_vim_mode(VimMode.DEFAULT)
            return True  # Consume the key to prevent accidental typing

        self.current_input += char

        # Filter hints that match current input
        matching_hints = [
            h for h in self.hints
            if h["hint"].startswith(self.current_input)
        ]

        # Check for exact match
        for hint in matching_hints:
            if hint["hint"] == self.current_input:
                # Found exact match, activate the widget
                self._activate_widget(hint["widget"])
                self.hide()
                from .modes import VimMode
                self.parent.set_vim_mode(VimMode.DEFAULT)
                return True

        # If no more matches possible, exit hint mode
        if not matching_hints:
            self.hide()
            from .modes import VimMode
            self.parent.set_vim_mode(VimMode.DEFAULT)
            return True

        # Update visual: hide non-matching hints
        self._update_hint_visibility()

        return True

    def _find_widgets(self, hint_type):
        """
        Find widgets based on hint type.

        Args:
            hint_type: 'input' for input fields only, 'all' for all clickable

        Returns:
            List of widgets to show hints on
        """
        widgets = []

        def traverse(widget):
            if not widget.IsShown() or not widget.IsEnabled():
                return

            if hint_type == "input":
                # Only input fields
                if isinstance(widget, (wx.TextCtrl, wx.ComboBox, wx.SearchCtrl)):
                    widgets.append(widget)
            else:  # 'all' - clickable elements
                if isinstance(widget, (
                    wx.Button, wx.BitmapButton, wx.ToggleButton,
                    wx.CheckBox, wx.RadioButton,
                    wx.ListCtrl, wx.Choice, wx.ComboBox,
                    wx.TextCtrl, wx.SearchCtrl  # Include inputs in 'all' mode too
                )):
                    widgets.append(widget)

            # Traverse children
            for child in widget.GetChildren():
                traverse(child)

        traverse(self.parent)
        return widgets

    def _generate_hint_string(self, index):
        """
        Generate a hint string for the given index.

        Uses single characters for first N elements (where N = len(hint_chars)),
        then two-character combinations for more elements.

        Args:
            index: The index of the element

        Returns:
            A hint string like 'a', 's', 'd', or 'aa', 'as', etc.
        """
        chars = self.hint_chars
        num_chars = len(chars)

        if index < num_chars:
            return chars[index]
        else:
            # Two-character hints
            first_idx = (index - num_chars) // num_chars
            second_idx = (index - num_chars) % num_chars
            if first_idx < num_chars:
                return chars[first_idx] + chars[second_idx]
            else:
                # Three-character hints (rare)
                third_idx = first_idx % num_chars
                first_idx = first_idx // num_chars
                return chars[first_idx] + chars[third_idx] + chars[second_idx]

    def _create_hint_window(self, widget, hint_str):
        """Create a hint label window on top of the widget."""
        # Get widget position relative to parent
        pos = widget.GetScreenPosition()
        parent_pos = self.parent.GetScreenPosition()
        relative_pos = (pos.x - parent_pos.x, pos.y - parent_pos.y)

        # Calculate size based on hint string length
        hint_width = max(20, 10 + len(hint_str) * 10)

        # Create a small panel for the hint
        hint_panel = wx.Panel(self.parent, pos=relative_pos, size=(hint_width, 20))
        hint_panel.SetBackgroundColour(wx.Colour(254, 218, 49))  # Yellow (#feda31)

        # Add text
        hint_text = wx.StaticText(hint_panel, label=hint_str.upper(), pos=(3, 2))
        font = hint_text.GetFont()
        font.PointSize = 10
        font = font.Bold()
        hint_text.SetFont(font)
        hint_text.SetForegroundColour(wx.Colour(74, 64, 14))  # Dark brown (#4a400e)

        # Raise to top
        hint_panel.Raise()

        self.hint_windows.append(hint_panel)

    def _update_hint_visibility(self):
        """Update visibility of hint windows based on current input."""
        for i, hint in enumerate(self.hints):
            if i < len(self.hint_windows):
                window = self.hint_windows[i]
                if hint["hint"].startswith(self.current_input):
                    window.Show()
                else:
                    window.Hide()

    def _activate_widget(self, widget):
        """
        Activate the selected widget.

        For buttons: simulate click
        For inputs: focus them
        For checkboxes: toggle and focus
        """
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
        elif isinstance(widget, wx.RadioButton):
            widget.SetValue(True)
            event = wx.CommandEvent(wx.wxEVT_COMMAND_RADIOBUTTON_SELECTED, widget.GetId())
            event.SetEventObject(widget)
            widget.GetEventHandler().ProcessEvent(event)
        elif isinstance(widget, (wx.TextCtrl, wx.ComboBox, wx.SearchCtrl)):
            # For input fields, just focus them
            widget.SetFocus()
        elif isinstance(widget, wx.ListCtrl):
            widget.SetFocus()
        elif isinstance(widget, wx.Choice):
            widget.SetFocus()

    def _clear_hints(self):
        """Clear all hint windows."""
        for window in self.hint_windows:
            window.Destroy()
        self.hint_windows = []
        self.hints = []
