"""
Protocol definitions for supyx backends.

All protocols use typing.Protocol for structural subtyping (duck typing).
Zero framework imports — backends implement these contracts using their
framework-specific types.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Protocol, Sequence, runtime_checkable


# ---------------------------------------------------------------------------
# Widget abstraction
# ---------------------------------------------------------------------------


@runtime_checkable
class WidgetHandle(Protocol):
    """Opaque handle to a framework widget.

    Core modules never inspect this directly — they pass it through
    to backend methods that know the concrete type.
    """

    ...


class WidgetInfo(Protocol):
    """Read-only metadata about a widget for hint/search logic."""

    @property
    def handle(self) -> Any: ...

    @property
    def widget_type(self) -> str:
        """One of: "input", "button", "checkbox", "radio", "list_item", "choice", "label"."""
        ...

    @property
    def text(self) -> str:
        """Display text or value (used for search matching)."""
        ...

    @property
    def is_visible(self) -> bool: ...

    @property
    def is_enabled(self) -> bool: ...


# ---------------------------------------------------------------------------
# Focus management
# ---------------------------------------------------------------------------


class FocusManager(Protocol):
    """Manages which widget has keyboard focus."""

    def get_focused(self) -> Optional[Any]:
        """Return the currently focused widget handle, or None."""
        ...

    def set_focus(self, widget: Any) -> None:
        """Set focus to the given widget."""
        ...

    def is_input_widget(self, widget: Any) -> bool:
        """Check if widget is a text input field."""
        ...

    def find_non_input_focusable(self) -> Optional[Any]:
        """Find a non-input widget that can accept focus (for ESC defocus)."""
        ...


# ---------------------------------------------------------------------------
# Widget discovery
# ---------------------------------------------------------------------------


class WidgetDiscovery(Protocol):
    """Discovers and interacts with widgets in the UI tree."""

    def find_widgets(self, widget_filter: str) -> Sequence[WidgetInfo]:
        """Find widgets matching a filter.

        Args:
            widget_filter: "input" for input fields only,
                          "all" for all clickable elements.
        """
        ...

    def get_text_content(self, widget: Any) -> str:
        """Get the text content/value of a widget."""
        ...

    def set_text_content(self, widget: Any, text: str) -> None:
        """Set the text content/value of a widget."""
        ...


# ---------------------------------------------------------------------------
# Widget activation
# ---------------------------------------------------------------------------


class WidgetActivator(Protocol):
    """Activates widgets (click, toggle, focus, etc.)."""

    def activate(self, widget: Any, widget_type: str) -> None:
        """Activate a widget based on its type.

        For buttons: simulate click.
        For inputs: focus them.
        For checkboxes: toggle and focus.
        For list items: select and trigger activation.
        """
        ...


# ---------------------------------------------------------------------------
# Overlay rendering
# ---------------------------------------------------------------------------


class HintRenderer(Protocol):
    """Renders hint labels on top of widgets."""

    def show_hint(self, widget: Any, hint_text: str) -> Any:
        """Show a hint label on/near the widget. Returns a handle for later removal."""
        ...

    def hide_hint(self, hint_handle: Any) -> None:
        """Remove a single hint label."""
        ...

    def hide_all(self) -> None:
        """Remove all hint labels."""
        ...

    def update_visibility(self, hint_handle: Any, visible: bool) -> None:
        """Show or hide a specific hint label."""
        ...


class SearchRenderer(Protocol):
    """Renders the search bar UI."""

    def show(self) -> None: ...

    def hide(self) -> None: ...

    def get_query(self) -> str: ...

    def set_info_text(self, text: str) -> None: ...

    def focus_search_input(self) -> None: ...

    def set_on_text_changed(self, callback: Callable[[str], None]) -> None: ...


# ---------------------------------------------------------------------------
# Scrolling
# ---------------------------------------------------------------------------


class ScrollManager(Protocol):
    """Manages scrolling behavior."""

    def scroll_lines(self, widget: Any, lines: int) -> None: ...

    def scroll_to_top(self, widget: Any) -> None: ...

    def scroll_to_bottom(self, widget: Any) -> None: ...

    def ensure_visible(self, widget: Any) -> None: ...


# ---------------------------------------------------------------------------
# Scheduling (deferred execution)
# ---------------------------------------------------------------------------


class Scheduler(Protocol):
    """Framework-specific deferred execution and timers."""

    def call_soon(self, callback: Callable[[], None]) -> None:
        """Schedule callback to run on the UI thread."""
        ...

    def call_later(self, delay_ms: int, callback: Callable[[], None]) -> Any:
        """Schedule callback after delay. Returns a cancellable handle."""
        ...

    def cancel_timer(self, handle: Any) -> None:
        """Cancel a previously scheduled timer."""
        ...


# ---------------------------------------------------------------------------
# Status and help display
# ---------------------------------------------------------------------------


class StatusDisplay(Protocol):
    """Displays vim mode status to the user."""

    def set_mode_text(self, text: str) -> None: ...


class HelpDisplay(Protocol):
    """Displays help/keybinding information."""

    def show_help(self, bindings_text: str) -> None: ...


# ---------------------------------------------------------------------------
# Editor integration
# ---------------------------------------------------------------------------


class EditorSuspender(Protocol):
    """Framework-specific UI suspension for launching $EDITOR."""

    def suspend_and_run(self, command: Sequence[str]) -> int:
        """Suspend the UI, run the command, resume. Returns exit code."""
        ...


# ---------------------------------------------------------------------------
# Clipboard
# ---------------------------------------------------------------------------


class ClipboardAccess(Protocol):
    """Framework-specific text clipboard access."""

    def get_text(self) -> Optional[str]: ...

    def set_text(self, text: str) -> None: ...


# ---------------------------------------------------------------------------
# Composite backend
# ---------------------------------------------------------------------------


class Backend(Protocol):
    """Aggregates all protocol implementations for a UI framework."""

    @property
    def focus_manager(self) -> FocusManager: ...

    @property
    def widget_discovery(self) -> WidgetDiscovery: ...

    @property
    def widget_activator(self) -> WidgetActivator: ...

    @property
    def hint_renderer(self) -> HintRenderer: ...

    @property
    def search_renderer(self) -> SearchRenderer: ...

    @property
    def scroll_manager(self) -> ScrollManager: ...

    @property
    def scheduler(self) -> Scheduler: ...

    @property
    def status_display(self) -> StatusDisplay: ...

    @property
    def help_display(self) -> HelpDisplay: ...

    @property
    def editor_suspender(self) -> EditorSuspender: ...

    @property
    def clipboard(self) -> ClipboardAccess: ...
