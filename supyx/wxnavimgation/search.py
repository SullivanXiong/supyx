"""
Search overlay for finding text in the application.
"""

import wx


class SearchOverlay:
    """
    Provides search functionality within the application.
    
    Displays a search bar and highlights matching text.
    """
    
    def __init__(self, parent):
        """
        Initialize the search overlay.
        
        Args:
            parent: The parent wx.Frame or window
        """
        self.parent = parent
        self.search_panel = None
        self.search_ctrl = None
        self.matches = []
        self.current_match_index = 0
    
    def show(self):
        """Show the search bar."""
        if self.search_panel:
            self.search_panel.Show()
            self.search_ctrl.SetFocus()
            return
        
        # Create search panel at bottom of window
        parent_size = self.parent.GetSize()
        self.search_panel = wx.Panel(
            self.parent,
            pos=(0, parent_size.height - 40),
            size=(parent_size.width, 40)
        )
        self.search_panel.SetBackgroundColour(wx.Colour(50, 50, 50))
        
        # Create search control
        label = wx.StaticText(self.search_panel, label="/", pos=(10, 10))
        label.SetForegroundColour(wx.Colour(255, 255, 255))
        
        self.search_ctrl = wx.SearchCtrl(
            self.search_panel,
            pos=(30, 5),
            size=(parent_size.width - 200, 30)
        )
        self.search_ctrl.ShowCancelButton(True)
        
        # Info label
        self.info_label = wx.StaticText(
            self.search_panel,
            label="0 matches",
            pos=(parent_size.width - 160, 10)
        )
        self.info_label.SetForegroundColour(wx.Colour(200, 200, 200))
        
        # Bind events
        self.search_ctrl.Bind(wx.EVT_TEXT, self._on_search_text)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._on_cancel)
        
        self.search_ctrl.SetFocus()
    
    def hide(self):
        """Hide the search bar."""
        if self.search_panel:
            self.search_panel.Hide()
        self._clear_highlights()
    
    def handle_key(self, keycode):
        """
        Handle key input in search mode.
        
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
        
        # Enter to search
        if keycode == wx.WXK_RETURN:
            self._search_next()
            return True
        
        # Let the search control handle other keys
        return False
    
    def _on_search_text(self, event):
        """Handle search text changes."""
        query = self.search_ctrl.GetValue()
        if query:
            self._search(query)
        else:
            self._clear_highlights()
            self.info_label.SetLabel("0 matches")
    
    def _on_cancel(self, event):
        """Handle cancel button."""
        self.hide()
        self.parent.set_vim_mode(self.parent.vim_mode.__class__.NORMAL)
    
    def _search(self, query):
        """
        Search for text in all text controls and labels.
        
        Args:
            query: The search query string
        """
        self._clear_highlights()
        self.matches = []
        
        query = query.lower()
        
        def search_widget(widget):
            if isinstance(widget, (wx.StaticText, wx.Button)):
                text = widget.GetLabelText().lower()
                if query in text:
                    self.matches.append(widget)
            elif isinstance(widget, wx.TextCtrl):
                text = widget.GetValue().lower()
                if query in text:
                    self.matches.append(widget)
            elif isinstance(widget, wx.ListCtrl):
                # Search in list items
                for i in range(widget.GetItemCount()):
                    for col in range(widget.GetColumnCount()):
                        text = widget.GetItemText(i, col).lower()
                        if query in text:
                            self.matches.append((widget, i))
                            break
            
            # Traverse children
            for child in widget.GetChildren():
                search_widget(child)
        
        search_widget(self.parent)
        
        # Update info label
        match_count = len(self.matches)
        self.info_label.SetLabel(f"{match_count} match{'es' if match_count != 1 else ''}")
        
        if self.matches:
            self.current_match_index = 0
            self._highlight_current_match()
    
    def _search_next(self):
        """Move to the next search match."""
        if not self.matches:
            return
        
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        self._highlight_current_match()
    
    def _highlight_current_match(self):
        """Highlight the current match."""
        if not self.matches:
            return
        
        match = self.matches[self.current_match_index]
        
        if isinstance(match, tuple):
            # ListCtrl item
            widget, item_index = match
            widget.SetFocus()
            widget.Select(item_index)
            widget.EnsureVisible(item_index)
        else:
            # Regular widget
            match.SetFocus()
            # Scroll to make it visible if possible
            parent = match.GetParent()
            if hasattr(parent, 'ScrollChildIntoView'):
                parent.ScrollChildIntoView(match)
        
        # Update info label
        self.info_label.SetLabel(
            f"{self.current_match_index + 1}/{len(self.matches)}"
        )
    
    def _clear_highlights(self):
        """Clear all search highlights."""
        self.matches = []
        self.current_match_index = 0

