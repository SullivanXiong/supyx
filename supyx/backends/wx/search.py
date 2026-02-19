"""
wxPython search overlay renderer.

Creates a search bar panel at the bottom of the window.
"""

from __future__ import annotations

from typing import Callable, Optional

import wx


class WxSearchRenderer:
    """Renders the search bar as a wx.Panel with wx.SearchCtrl."""

    def __init__(self, parent: wx.Frame) -> None:
        self._parent = parent
        self._panel: Optional[wx.Panel] = None
        self._search_ctrl: Optional[wx.SearchCtrl] = None
        self._info_label: Optional[wx.StaticText] = None
        self._on_text_changed: Optional[Callable[[str], None]] = None

    def show(self) -> None:
        """Show the search bar."""
        if self._panel is not None:
            self._panel.Show()
            if self._search_ctrl:
                self._search_ctrl.SetFocus()
            return

        parent_size = self._parent.GetSize()
        self._panel = wx.Panel(
            self._parent,
            pos=(0, parent_size.height - 40),
            size=(parent_size.width, 40),
        )
        self._panel.SetBackgroundColour(wx.Colour(50, 50, 50))

        label = wx.StaticText(self._panel, label="/", pos=(10, 10))
        label.SetForegroundColour(wx.Colour(255, 255, 255))

        self._search_ctrl = wx.SearchCtrl(
            self._panel,
            pos=(30, 5),
            size=(parent_size.width - 200, 30),
        )
        self._search_ctrl.ShowCancelButton(True)

        self._info_label = wx.StaticText(
            self._panel,
            label="0 matches",
            pos=(parent_size.width - 160, 10),
        )
        self._info_label.SetForegroundColour(wx.Colour(200, 200, 200))

        # Bind events
        self._search_ctrl.Bind(wx.EVT_TEXT, self._on_text_event)
        self._search_ctrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._on_cancel)

        self._search_ctrl.SetFocus()

    def hide(self) -> None:
        """Hide the search bar."""
        if self._panel is not None:
            self._panel.Hide()

    def get_query(self) -> str:
        """Get the current search query text."""
        if self._search_ctrl:
            return self._search_ctrl.GetValue()
        return ""

    def set_info_text(self, text: str) -> None:
        """Update the match count/info label."""
        if self._info_label:
            self._info_label.SetLabel(text)

    def focus_search_input(self) -> None:
        """Focus the search text input."""
        if self._search_ctrl:
            self._search_ctrl.SetFocus()

    def set_on_text_changed(self, callback: Callable[[str], None]) -> None:
        """Register a callback for live search text changes."""
        self._on_text_changed = callback

    def _on_text_event(self, event: wx.Event) -> None:
        """Handle wx.EVT_TEXT from the search control."""
        if self._on_text_changed and self._search_ctrl:
            self._on_text_changed(self._search_ctrl.GetValue())

    def _on_cancel(self, event: wx.Event) -> None:
        """Handle cancel button click."""
        self.hide()
