"""
wxPython widget discovery, focus management, activation, scrolling, and display.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence

import wx


# ---------------------------------------------------------------------------
# WidgetInfo implementation
# ---------------------------------------------------------------------------


@dataclass
class WxWidgetInfo:
    """WidgetInfo implementation for wxPython widgets."""

    handle: Any  # wx.Window or (wx.ListCtrl, int) tuple
    widget_type: str
    text: str
    is_visible: bool
    is_enabled: bool


# ---------------------------------------------------------------------------
# WidgetDiscovery
# ---------------------------------------------------------------------------


class WxWidgetDiscovery:
    """Discovers widgets in the wxPython widget tree."""

    def __init__(self, parent: wx.Frame) -> None:
        self._parent = parent

    def find_widgets(self, widget_filter: str) -> Sequence[WxWidgetInfo]:
        """Find widgets matching a filter."""
        widgets: list[WxWidgetInfo] = []

        def traverse(widget: wx.Window) -> None:
            if not widget.IsShown() or not widget.IsEnabled():
                return

            if widget_filter == "input":
                if isinstance(widget, (wx.TextCtrl, wx.ComboBox, wx.SearchCtrl)):
                    widgets.append(
                        WxWidgetInfo(
                            handle=widget,
                            widget_type="input",
                            text=widget.GetValue() if hasattr(widget, "GetValue") else "",
                            is_visible=True,
                            is_enabled=True,
                        )
                    )
            else:  # "all"
                if isinstance(widget, wx.ListCtrl):
                    for i in range(widget.GetItemCount()):
                        item_text = widget.GetItemText(i, 1) if widget.GetColumnCount() > 1 else widget.GetItemText(i)
                        widgets.append(
                            WxWidgetInfo(
                                handle=(widget, i),
                                widget_type="list_item",
                                text=item_text,
                                is_visible=True,
                                is_enabled=True,
                            )
                        )
                elif isinstance(widget, (wx.Button, wx.BitmapButton, wx.ToggleButton)):
                    widgets.append(
                        WxWidgetInfo(
                            handle=widget,
                            widget_type="button",
                            text=widget.GetLabelText(),
                            is_visible=True,
                            is_enabled=True,
                        )
                    )
                elif isinstance(widget, wx.CheckBox):
                    widgets.append(
                        WxWidgetInfo(
                            handle=widget,
                            widget_type="checkbox",
                            text=widget.GetLabelText(),
                            is_visible=True,
                            is_enabled=True,
                        )
                    )
                elif isinstance(widget, wx.RadioButton):
                    widgets.append(
                        WxWidgetInfo(
                            handle=widget,
                            widget_type="radio",
                            text=widget.GetLabelText(),
                            is_visible=True,
                            is_enabled=True,
                        )
                    )
                elif isinstance(widget, wx.Choice):
                    widgets.append(
                        WxWidgetInfo(
                            handle=widget,
                            widget_type="choice",
                            text="",
                            is_visible=True,
                            is_enabled=True,
                        )
                    )
                elif isinstance(widget, (wx.TextCtrl, wx.ComboBox, wx.SearchCtrl)):
                    widgets.append(
                        WxWidgetInfo(
                            handle=widget,
                            widget_type="input",
                            text=widget.GetValue() if hasattr(widget, "GetValue") else "",
                            is_visible=True,
                            is_enabled=True,
                        )
                    )
                elif isinstance(widget, wx.StaticText):
                    widgets.append(
                        WxWidgetInfo(
                            handle=widget,
                            widget_type="label",
                            text=widget.GetLabelText(),
                            is_visible=True,
                            is_enabled=True,
                        )
                    )

            for child in widget.GetChildren():
                traverse(child)

        traverse(self._parent)
        return widgets

    def get_text_content(self, widget: Any) -> str:
        """Get text content of a widget."""
        if isinstance(widget, tuple):
            list_ctrl, idx = widget
            return list_ctrl.GetItemText(idx)
        if hasattr(widget, "GetValue"):
            return widget.GetValue()
        if hasattr(widget, "GetLabelText"):
            return widget.GetLabelText()
        return ""

    def set_text_content(self, widget: Any, text: str) -> None:
        """Set text content of a widget."""
        if hasattr(widget, "SetValue"):
            widget.SetValue(text)


# ---------------------------------------------------------------------------
# FocusManager
# ---------------------------------------------------------------------------


class WxFocusManager:
    """Manages focus for wxPython widgets."""

    def __init__(self, parent: wx.Frame) -> None:
        self._parent = parent

    def get_focused(self) -> Optional[Any]:
        return wx.Window.FindFocus()

    def set_focus(self, widget: Any) -> None:
        if isinstance(widget, tuple):
            list_ctrl, idx = widget
            list_ctrl.Select(idx)
            list_ctrl.Focus(idx)
            list_ctrl.SetFocus()
        elif hasattr(widget, "SetFocus"):
            # Use CallLater for macOS compatibility
            wx.CallLater(10, widget.SetFocus)

    def is_input_widget(self, widget: Any) -> bool:
        return isinstance(widget, (wx.TextCtrl, wx.ComboBox, wx.SearchCtrl))

    def find_non_input_focusable(self) -> Optional[Any]:
        def find(window: wx.Window) -> Optional[wx.Window]:
            for child in window.GetChildren():
                if isinstance(child, wx.ListCtrl):
                    return child
                result = find(child)
                if result:
                    return result
            return None

        return find(self._parent)


# ---------------------------------------------------------------------------
# WidgetActivator
# ---------------------------------------------------------------------------


class WxWidgetActivator:
    """Activates wxPython widgets."""

    def activate(self, widget: Any, widget_type: str) -> None:
        if isinstance(widget, tuple):
            list_ctrl, item_index = widget
            list_ctrl.Select(item_index)
            list_ctrl.Focus(item_index)
            list_ctrl.SetFocus()
            event = wx.ListEvent(wx.wxEVT_LIST_ITEM_ACTIVATED, list_ctrl.GetId())
            event.SetIndex(item_index)
            event.SetEventObject(list_ctrl)
            list_ctrl.GetEventHandler().ProcessEvent(event)
            return

        if widget_type == "button":
            event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, widget.GetId())
            event.SetEventObject(widget)
            widget.GetEventHandler().ProcessEvent(event)
        elif widget_type == "checkbox":
            widget.SetValue(not widget.GetValue())
            event = wx.CommandEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED, widget.GetId())
            event.SetEventObject(widget)
            widget.GetEventHandler().ProcessEvent(event)
        elif widget_type == "radio":
            widget.SetValue(True)
            event = wx.CommandEvent(wx.wxEVT_COMMAND_RADIOBUTTON_SELECTED, widget.GetId())
            event.SetEventObject(widget)
            widget.GetEventHandler().ProcessEvent(event)
        elif widget_type in ("input", "choice"):
            widget.SetFocus()
        elif widget_type == "list_item":
            widget.SetFocus()


# ---------------------------------------------------------------------------
# ScrollManager
# ---------------------------------------------------------------------------


class WxScrollManager:
    """Scroll management for wxPython."""

    def __init__(self, parent: wx.Frame) -> None:
        self._parent = parent

    def scroll_lines(self, widget: Any, lines: int) -> None:
        target = widget if hasattr(widget, "ScrollLines") else self._parent
        if hasattr(target, "ScrollLines"):
            target.ScrollLines(lines)

    def scroll_to_top(self, widget: Any) -> None:
        target = widget if hasattr(widget, "Scroll") else self._parent
        if hasattr(target, "Scroll"):
            target.Scroll(0, 0)

    def scroll_to_bottom(self, widget: Any) -> None:
        target = widget if hasattr(widget, "GetScrollRange") else self._parent
        if hasattr(target, "GetScrollRange") and hasattr(target, "Scroll"):
            max_y = target.GetScrollRange(wx.VERTICAL)
            target.Scroll(0, max_y)

    def ensure_visible(self, widget: Any) -> None:
        if isinstance(widget, tuple):
            list_ctrl, idx = widget
            list_ctrl.EnsureVisible(idx)
        elif hasattr(widget, "GetParent"):
            parent = widget.GetParent()
            if hasattr(parent, "ScrollChildIntoView"):
                parent.ScrollChildIntoView(widget)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------


class WxScheduler:
    """Deferred execution using wx timers."""

    def call_soon(self, callback: Callable[[], None]) -> None:
        wx.CallAfter(callback)

    def call_later(self, delay_ms: int, callback: Callable[[], None]) -> Any:
        return wx.CallLater(delay_ms, callback)

    def cancel_timer(self, handle: Any) -> None:
        if handle is not None and hasattr(handle, "Stop"):
            handle.Stop()


# ---------------------------------------------------------------------------
# StatusDisplay
# ---------------------------------------------------------------------------


class WxStatusDisplay:
    """Shows mode text in the wx status bar."""

    def __init__(self, parent: wx.Frame) -> None:
        self._parent = parent

    def set_mode_text(self, text: str) -> None:
        status_bar = self._parent.GetStatusBar()
        if not status_bar:
            return
        if status_bar.GetFieldsCount() > 1:
            status_bar.SetStatusText(text, 1)
        else:
            status_bar.SetFieldsCount(2)
            status_bar.SetStatusWidths([-1, 150])
            status_bar.SetStatusText(text, 1)


# ---------------------------------------------------------------------------
# HelpDisplay
# ---------------------------------------------------------------------------


class WxHelpDisplay:
    """Shows help dialog in wx."""

    def __init__(self, parent: wx.Frame) -> None:
        self._parent = parent

    def show_help(self, bindings_text: str) -> None:
        dlg = wx.MessageDialog(
            self._parent,
            bindings_text,
            "Keyboard Shortcuts",
            wx.OK | wx.ICON_INFORMATION,
        )
        dlg.ShowModal()
        dlg.Destroy()


# ---------------------------------------------------------------------------
# EditorSuspender
# ---------------------------------------------------------------------------


class WxEditorSuspender:
    """Blocks wx event loop to run $EDITOR."""

    def suspend_and_run(self, command: list[str]) -> int:
        result = subprocess.run(command)
        return result.returncode


# ---------------------------------------------------------------------------
# ClipboardAccess
# ---------------------------------------------------------------------------


class WxClipboardAccess:
    """Text clipboard access for wxPython."""

    def get_text(self) -> Optional[str]:
        if not wx.TheClipboard.Open():
            return None
        try:
            data = wx.TextDataObject()
            if wx.TheClipboard.GetData(data):
                return data.GetText()
            return None
        finally:
            wx.TheClipboard.Close()

    def set_text(self, text: str) -> None:
        if not wx.TheClipboard.Open():
            return
        try:
            wx.TheClipboard.SetData(wx.TextDataObject(text))
        finally:
            wx.TheClipboard.Close()
