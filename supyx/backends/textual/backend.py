"""
Textual backend — aggregates all protocol implementations.
"""

from __future__ import annotations

from textual.app import App

from .hints import TextualHintRenderer
from .search import TextualSearchRenderer
from .widgets import (
    TextualClipboardAccess,
    TextualEditorSuspender,
    TextualFocusManager,
    TextualHelpDisplay,
    TextualScheduler,
    TextualScrollManager,
    TextualStatusDisplay,
    TextualWidgetActivator,
    TextualWidgetDiscovery,
)


class TextualBackend:
    """Aggregates all Textual-specific protocol implementations."""

    def __init__(self, app: App) -> None:
        self._focus_manager = TextualFocusManager(app)
        self._widget_discovery = TextualWidgetDiscovery(app)
        self._widget_activator = TextualWidgetActivator()
        self._hint_renderer = TextualHintRenderer(app)
        self._search_renderer = TextualSearchRenderer(app)
        self._scroll_manager = TextualScrollManager(app)
        self._scheduler = TextualScheduler(app)
        self._status_display = TextualStatusDisplay(app)
        self._help_display = TextualHelpDisplay(app)
        self._editor_suspender = TextualEditorSuspender(app)
        self._clipboard = TextualClipboardAccess()

    @property
    def focus_manager(self) -> TextualFocusManager:
        return self._focus_manager

    @property
    def widget_discovery(self) -> TextualWidgetDiscovery:
        return self._widget_discovery

    @property
    def widget_activator(self) -> TextualWidgetActivator:
        return self._widget_activator

    @property
    def hint_renderer(self) -> TextualHintRenderer:
        return self._hint_renderer

    @property
    def search_renderer(self) -> TextualSearchRenderer:
        return self._search_renderer

    @property
    def scroll_manager(self) -> TextualScrollManager:
        return self._scroll_manager

    @property
    def scheduler(self) -> TextualScheduler:
        return self._scheduler

    @property
    def status_display(self) -> TextualStatusDisplay:
        return self._status_display

    @property
    def help_display(self) -> TextualHelpDisplay:
        return self._help_display

    @property
    def editor_suspender(self) -> TextualEditorSuspender:
        return self._editor_suspender

    @property
    def clipboard(self) -> TextualClipboardAccess:
        return self._clipboard
