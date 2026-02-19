"""
Textual widget discovery, focus management, activation, scrolling, and display.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence

from textual.app import App
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import (
    Button,
    Checkbox,
    Input,
    Label,
    RadioButton,
    Select,
    Static,
    Switch,
    TextArea,
)


# ---------------------------------------------------------------------------
# WidgetInfo implementation
# ---------------------------------------------------------------------------


@dataclass
class TextualWidgetInfo:
    """WidgetInfo implementation for Textual widgets."""

    handle: Any  # Textual Widget
    widget_type: str
    text: str
    is_visible: bool
    is_enabled: bool


# ---------------------------------------------------------------------------
# WidgetDiscovery
# ---------------------------------------------------------------------------


_INPUT_TYPES = (Input, TextArea)
_BUTTON_TYPES = (Button,)
_TOGGLE_TYPES = (Checkbox, Switch, RadioButton)


class TextualWidgetDiscovery:
    """Discovers widgets in the Textual widget tree."""

    def __init__(self, app: App) -> None:
        self._app = app

    def find_widgets(self, widget_filter: str) -> Sequence[TextualWidgetInfo]:
        """Find widgets matching a filter."""
        widgets: list[TextualWidgetInfo] = []

        if widget_filter == "input":
            for widget in self._app.query("Input, TextArea"):
                if widget.display and not widget.disabled:
                    widgets.append(
                        TextualWidgetInfo(
                            handle=widget,
                            widget_type="input",
                            text=self._get_widget_text(widget),
                            is_visible=True,
                            is_enabled=True,
                        )
                    )
        else:  # "all"
            for widget in self._app.query("*"):
                if not widget.display or widget.disabled:
                    continue
                if not widget.focusable:
                    continue

                wtype = self._classify_widget(widget)
                if wtype:
                    widgets.append(
                        TextualWidgetInfo(
                            handle=widget,
                            widget_type=wtype,
                            text=self._get_widget_text(widget),
                            is_visible=True,
                            is_enabled=True,
                        )
                    )

        return widgets

    def get_text_content(self, widget: Any) -> str:
        """Get text content of a widget."""
        return self._get_widget_text(widget)

    def set_text_content(self, widget: Any, text: str) -> None:
        """Set text content of a widget."""
        if isinstance(widget, Input):
            widget.value = text
        elif isinstance(widget, TextArea):
            widget.clear()
            widget.insert(text)

    @staticmethod
    def _get_widget_text(widget: Widget) -> str:
        if isinstance(widget, (Input, TextArea)):
            return widget.value if hasattr(widget, "value") else ""
        if isinstance(widget, (Button, Label, Static)):
            renderable = widget.renderable
            return str(renderable) if renderable else ""
        return ""

    @staticmethod
    def _classify_widget(widget: Widget) -> Optional[str]:
        if isinstance(widget, _INPUT_TYPES):
            return "input"
        if isinstance(widget, _BUTTON_TYPES):
            return "button"
        if isinstance(widget, (Checkbox, Switch)):
            return "checkbox"
        if isinstance(widget, RadioButton):
            return "radio"
        if isinstance(widget, Select):
            return "choice"
        if isinstance(widget, (Label, Static)):
            return "label"
        return None


# ---------------------------------------------------------------------------
# FocusManager
# ---------------------------------------------------------------------------


class TextualFocusManager:
    """Manages focus for Textual widgets."""

    def __init__(self, app: App) -> None:
        self._app = app

    def get_focused(self) -> Optional[Any]:
        return self._app.focused

    def set_focus(self, widget: Any) -> None:
        if isinstance(widget, Widget):
            widget.focus()

    def is_input_widget(self, widget: Any) -> bool:
        return isinstance(widget, _INPUT_TYPES)

    def find_non_input_focusable(self) -> Optional[Any]:
        for widget in self._app.query("*"):
            if widget.focusable and not isinstance(widget, _INPUT_TYPES):
                return widget
        return None


# ---------------------------------------------------------------------------
# WidgetActivator
# ---------------------------------------------------------------------------


class TextualWidgetActivator:
    """Activates Textual widgets."""

    def activate(self, widget: Any, widget_type: str) -> None:
        if widget_type == "button" and isinstance(widget, Button):
            widget.press()
        elif widget_type == "checkbox":
            if isinstance(widget, Switch):
                widget.toggle()
            elif isinstance(widget, Checkbox):
                widget.toggle()
            widget.focus()
        elif widget_type == "radio" and isinstance(widget, RadioButton):
            widget.toggle()
            widget.focus()
        elif widget_type in ("input", "choice"):
            widget.focus()
        elif widget_type == "label":
            widget.focus()


# ---------------------------------------------------------------------------
# ScrollManager
# ---------------------------------------------------------------------------


class TextualScrollManager:
    """Scroll management for Textual."""

    def __init__(self, app: App) -> None:
        self._app = app

    def scroll_lines(self, widget: Any, lines: int) -> None:
        target = widget if hasattr(widget, "scroll_relative") else self._app.screen
        if hasattr(target, "scroll_relative"):
            target.scroll_relative(y=lines, animate=False)

    def scroll_to_top(self, widget: Any) -> None:
        target = widget if hasattr(widget, "scroll_home") else self._app.screen
        if hasattr(target, "scroll_home"):
            target.scroll_home(animate=False)

    def scroll_to_bottom(self, widget: Any) -> None:
        target = widget if hasattr(widget, "scroll_end") else self._app.screen
        if hasattr(target, "scroll_end"):
            target.scroll_end(animate=False)

    def ensure_visible(self, widget: Any) -> None:
        if isinstance(widget, Widget) and hasattr(widget, "scroll_visible"):
            widget.scroll_visible(animate=False)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------


class TextualScheduler:
    """Deferred execution using Textual timers."""

    def __init__(self, app: App) -> None:
        self._app = app

    def call_soon(self, callback: Callable[[], None]) -> None:
        self._app.call_later(callback)

    def call_later(self, delay_ms: int, callback: Callable[[], None]) -> Any:
        return self._app.set_timer(delay_ms / 1000.0, callback)

    def cancel_timer(self, handle: Any) -> None:
        if isinstance(handle, Timer):
            handle.stop()


# ---------------------------------------------------------------------------
# StatusDisplay
# ---------------------------------------------------------------------------


class TextualStatusDisplay:
    """Shows mode text via a Static widget or app title."""

    def __init__(self, app: App) -> None:
        self._app = app
        self._status_widget: Optional[Static] = None

    def set_mode_text(self, text: str) -> None:
        # Try to find a dedicated status widget
        if self._status_widget is None:
            try:
                self._status_widget = self._app.query_one("#vim-status", Static)
            except Exception:
                pass

        if self._status_widget is not None:
            self._status_widget.update(text)
        else:
            # Fall back to app sub_title
            self._app.sub_title = text


# ---------------------------------------------------------------------------
# HelpDisplay
# ---------------------------------------------------------------------------


class TextualHelpDisplay:
    """Shows help via Textual notification."""

    def __init__(self, app: App) -> None:
        self._app = app

    def show_help(self, bindings_text: str) -> None:
        self._app.notify(bindings_text, timeout=10)


# ---------------------------------------------------------------------------
# EditorSuspender
# ---------------------------------------------------------------------------


class TextualEditorSuspender:
    """Suspends Textual app to run $EDITOR."""

    def __init__(self, app: App) -> None:
        self._app = app

    def suspend_and_run(self, command: list[str]) -> int:
        with self._app.suspend():
            result = subprocess.run(command)
            return result.returncode


# ---------------------------------------------------------------------------
# ClipboardAccess
# ---------------------------------------------------------------------------


class TextualClipboardAccess:
    """Text clipboard access (OS-level, no framework dependency)."""

    def get_text(self) -> Optional[str]:
        try:
            import platform

            if platform.system() == "Darwin":
                result = subprocess.run(
                    ["pbpaste"], capture_output=True, text=True
                )
                return result.stdout if result.returncode == 0 else None
            else:
                result = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-o"],
                    capture_output=True,
                    text=True,
                )
                return result.stdout if result.returncode == 0 else None
        except Exception:
            return None

    def set_text(self, text: str) -> None:
        try:
            import platform

            if platform.system() == "Darwin":
                subprocess.run(["pbcopy"], input=text, text=True)
            else:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text,
                    text=True,
                )
        except Exception:
            pass
