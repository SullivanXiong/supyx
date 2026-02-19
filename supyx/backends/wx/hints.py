"""
wxPython hint overlay renderer.

Creates wx.Panel overlays with hint labels on top of widgets.
"""

from __future__ import annotations

from typing import Any

import wx


class WxHintRenderer:
    """Renders hint labels as wx.Panel overlays."""

    def __init__(self, parent: wx.Frame) -> None:
        self._parent = parent
        self._hint_windows: list[wx.Panel] = []

    def show_hint(self, widget: Any, hint_text: str) -> wx.Panel:
        """Create a hint label on/near the widget. Returns the panel handle."""
        hint_width = 8 + len(hint_text) * 8
        hint_height = 16

        # Calculate position
        if isinstance(widget, tuple):
            list_ctrl, item_index = widget
            item_rect = list_ctrl.GetItemRect(item_index)
            item_screen_x, item_screen_y = list_ctrl.ClientToScreen(
                (item_rect.x, item_rect.y)
            )
            parent_client_x, parent_client_y = self._parent.ClientToScreen((0, 0))
            relative_pos = (
                item_screen_x - parent_client_x + 5,
                item_screen_y - parent_client_y + (item_rect.height - hint_height) // 2,
            )
        else:
            pos = widget.GetScreenPosition()
            size = widget.GetSize()
            parent_client_x, parent_client_y = self._parent.ClientToScreen((0, 0))
            relative_pos = (
                pos.x - parent_client_x + (size.width - hint_width) // 2,
                pos.y - parent_client_y + (size.height - hint_height) // 2,
            )

        # Create hint panel
        hint_panel = wx.Panel(
            self._parent, pos=relative_pos, size=(hint_width, hint_height)
        )
        hint_panel.SetBackgroundColour(wx.Colour(254, 218, 49))  # Yellow

        # Add centered text
        hint_label = wx.StaticText(hint_panel, label=hint_text.upper())
        font = hint_label.GetFont()
        font.PointSize = 9
        font = font.Bold()
        hint_label.SetFont(font)
        hint_label.SetForegroundColour(wx.Colour(74, 64, 14))  # Dark brown

        text_size = hint_label.GetSize()
        hint_label.SetPosition(
            (
                (hint_width - text_size.width) // 2,
                (hint_height - text_size.height) // 2,
            )
        )

        hint_panel.Raise()
        self._hint_windows.append(hint_panel)
        return hint_panel

    def hide_hint(self, hint_handle: Any) -> None:
        """Remove a single hint panel."""
        if isinstance(hint_handle, wx.Panel):
            hint_handle.Destroy()
            if hint_handle in self._hint_windows:
                self._hint_windows.remove(hint_handle)

    def hide_all(self) -> None:
        """Remove all hint panels."""
        for window in self._hint_windows:
            window.Destroy()
        self._hint_windows = []

    def update_visibility(self, hint_handle: Any, visible: bool) -> None:
        """Show or hide a specific hint panel."""
        if isinstance(hint_handle, wx.Panel):
            if visible:
                hint_handle.Show()
            else:
                hint_handle.Hide()
