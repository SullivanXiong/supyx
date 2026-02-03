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
            List of widgets/items to show hints on. For ListCtrl items,
            returns tuples of (ListCtrl, item_index).
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
                if isinstance(widget, wx.ListCtrl):
                    # Add individual list items instead of the whole ListCtrl
                    item_count = widget.GetItemCount()
                    for i in range(item_count):
                        widgets.append((widget, i))  # Tuple: (ListCtrl, item_index)
                elif isinstance(widget, (
                    wx.Button, wx.BitmapButton, wx.ToggleButton,
                    wx.CheckBox, wx.RadioButton,
                    wx.Choice, wx.ComboBox,
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

    def _create_hint_window(self, widget_or_item, hint_str):
        """Create a hint label window on top of the widget or list item."""
        # Calculate size based on hint string length
        hint_width = 8 + len(hint_str) * 8
        hint_height = 16

        # Handle ListCtrl items (tuples of (ListCtrl, item_index))
        if isinstance(widget_or_item, tuple):
            list_ctrl, item_index = widget_or_item
            # Get item rect (relative to ListCtrl client area)
            item_rect = list_ctrl.GetItemRect(item_index)
            # Convert item position to screen coordinates
            item_screen_x, item_screen_y = list_ctrl.ClientToScreen((item_rect.x, item_rect.y))
            # Get parent's client area screen position (excludes title bar)
            parent_client_x, parent_client_y = self.parent.ClientToScreen((0, 0))
            # Position hint on the checkbox (first column)
            relative_pos = (
                item_screen_x - parent_client_x + 5,
                item_screen_y - parent_client_y + (item_rect.height - hint_height) // 2
            )
        else:
            # Regular widget
            pos = widget_or_item.GetScreenPosition()
            size = widget_or_item.GetSize()
            # Get parent's client area screen position (excludes title bar)
            parent_client_x, parent_client_y = self.parent.ClientToScreen((0, 0))
            # Center hint on the widget
            relative_pos = (
                pos.x - parent_client_x + (size.width - hint_width) // 2,
                pos.y - parent_client_y + (size.height - hint_height) // 2
            )

        # Create a small panel for the hint
        hint_panel = wx.Panel(self.parent, pos=relative_pos, size=(hint_width, hint_height))
        hint_panel.SetBackgroundColour(wx.Colour(254, 218, 49))  # Yellow (#feda31)

        # Add centered text
        hint_text = wx.StaticText(hint_panel, label=hint_str.upper())
        font = hint_text.GetFont()
        font.PointSize = 9
        font = font.Bold()
        hint_text.SetFont(font)
        hint_text.SetForegroundColour(wx.Colour(74, 64, 14))  # Dark brown (#4a400e)

        # Center text in panel
        text_size = hint_text.GetSize()
        hint_text.SetPosition((
            (hint_width - text_size.width) // 2,
            (hint_height - text_size.height) // 2
        ))

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

    def _activate_widget(self, widget_or_item):
        """
        Activate the selected widget or list item.

        For buttons: simulate click
        For inputs: focus them
        For checkboxes: toggle and focus
        For list items: select and trigger double-click (activation)
        """
        # Handle ListCtrl items (tuples of (ListCtrl, item_index))
        if isinstance(widget_or_item, tuple):
            list_ctrl, item_index = widget_or_item
            # Select the item
            list_ctrl.Select(item_index)
            list_ctrl.Focus(item_index)
            list_ctrl.SetFocus()
            # Trigger item activated event (like double-click)
            event = wx.ListEvent(wx.wxEVT_LIST_ITEM_ACTIVATED, list_ctrl.GetId())
            event.SetIndex(item_index)
            event.SetEventObject(list_ctrl)
            list_ctrl.GetEventHandler().ProcessEvent(event)
            return

        widget = widget_or_item
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
