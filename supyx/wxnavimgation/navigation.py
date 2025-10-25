"""
Navigation helpers for moving between UI elements.
"""

import wx


class NavigationHelper:
    """
    Helper class for navigating between UI elements.
    
    Provides functions for focusing inputs, moving between controls, etc.
    """
    
    def __init__(self, parent):
        """
        Initialize the navigation helper.
        
        Args:
            parent: The parent wx.Frame or window
        """
        self.parent = parent
        self.input_fields = []
        self.current_input_index = 0
    
    def focus_first_input(self):
        """Focus the first input field in the window."""
        self._update_input_list()
        if self.input_fields:
            self.input_fields[0].SetFocus()
            self.current_input_index = 0
    
    def focus_next_input(self):
        """Focus the next input field (gi command)."""
        self._update_input_list()
        if not self.input_fields:
            return
        
        self.current_input_index = (self.current_input_index + 1) % len(self.input_fields)
        self.input_fields[self.current_input_index].SetFocus()
    
    def focus_previous_input(self):
        """Focus the previous input field."""
        self._update_input_list()
        if not self.input_fields:
            return
        
        self.current_input_index = (self.current_input_index - 1) % len(self.input_fields)
        self.input_fields[self.current_input_index].SetFocus()
    
    def get_input_fields(self):
        """Get all input fields in the window."""
        self._update_input_list()
        return list(self.input_fields)
    
    def _update_input_list(self):
        """Update the list of input fields."""
        self.input_fields = []
        
        def find_inputs(widget):
            if widget.IsShown() and widget.IsEnabled():
                if isinstance(widget, (wx.TextCtrl, wx.ComboBox, wx.SearchCtrl)):
                    self.input_fields.append(widget)
                
                # Traverse children
                for child in widget.GetChildren():
                    find_inputs(child)
        
        find_inputs(self.parent)
    
    def scroll_up(self):
        """Scroll up if the window is scrollable."""
        focused = wx.Window.FindFocus()
        if hasattr(focused, 'ScrollLines'):
            focused.ScrollLines(-3)
        elif hasattr(self.parent, 'ScrollLines'):
            self.parent.ScrollLines(-3)
    
    def scroll_down(self):
        """Scroll down if the window is scrollable."""
        focused = wx.Window.FindFocus()
        if hasattr(focused, 'ScrollLines'):
            focused.ScrollLines(3)
        elif hasattr(self.parent, 'ScrollLines'):
            self.parent.ScrollLines(3)
    
    def go_to_top(self):
        """Scroll to the top of the window."""
        focused = wx.Window.FindFocus()
        if hasattr(focused, 'Scroll'):
            focused.Scroll(0, 0)
        elif hasattr(self.parent, 'Scroll'):
            self.parent.Scroll(0, 0)
    
    def go_to_bottom(self):
        """Scroll to the bottom of the window."""
        focused = wx.Window.FindFocus()
        if hasattr(focused, 'GetScrollRange') and hasattr(focused, 'Scroll'):
            max_y = focused.GetScrollRange(wx.VERTICAL)
            focused.Scroll(0, max_y)
        elif hasattr(self.parent, 'GetScrollRange') and hasattr(self.parent, 'Scroll'):
            max_y = self.parent.GetScrollRange(wx.VERTICAL)
            self.parent.Scroll(0, max_y)

