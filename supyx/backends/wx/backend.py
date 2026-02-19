"""
wxPython backend — aggregates all protocol implementations.
"""

from __future__ import annotations

import wx

from .hints import WxHintRenderer
from .search import WxSearchRenderer
from .widgets import (
    WxClipboardAccess,
    WxEditorSuspender,
    WxFocusManager,
    WxHelpDisplay,
    WxScheduler,
    WxScrollManager,
    WxStatusDisplay,
    WxWidgetActivator,
    WxWidgetDiscovery,
)


class WxBackend:
    """Aggregates all wx-specific protocol implementations."""

    def __init__(self, frame: wx.Frame) -> None:
        self._focus_manager = WxFocusManager(frame)
        self._widget_discovery = WxWidgetDiscovery(frame)
        self._widget_activator = WxWidgetActivator()
        self._hint_renderer = WxHintRenderer(frame)
        self._search_renderer = WxSearchRenderer(frame)
        self._scroll_manager = WxScrollManager(frame)
        self._scheduler = WxScheduler()
        self._status_display = WxStatusDisplay(frame)
        self._help_display = WxHelpDisplay(frame)
        self._editor_suspender = WxEditorSuspender()
        self._clipboard = WxClipboardAccess()

    @property
    def focus_manager(self) -> WxFocusManager:
        return self._focus_manager

    @property
    def widget_discovery(self) -> WxWidgetDiscovery:
        return self._widget_discovery

    @property
    def widget_activator(self) -> WxWidgetActivator:
        return self._widget_activator

    @property
    def hint_renderer(self) -> WxHintRenderer:
        return self._hint_renderer

    @property
    def search_renderer(self) -> WxSearchRenderer:
        return self._search_renderer

    @property
    def scroll_manager(self) -> WxScrollManager:
        return self._scroll_manager

    @property
    def scheduler(self) -> WxScheduler:
        return self._scheduler

    @property
    def status_display(self) -> WxStatusDisplay:
        return self._status_display

    @property
    def help_display(self) -> WxHelpDisplay:
        return self._help_display

    @property
    def editor_suspender(self) -> WxEditorSuspender:
        return self._editor_suspender

    @property
    def clipboard(self) -> WxClipboardAccess:
        return self._clipboard
