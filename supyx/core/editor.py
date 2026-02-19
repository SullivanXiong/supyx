"""
Framework-agnostic $EDITOR launcher.

Opens the user's preferred editor ($EDITOR or $VISUAL) on a temp file
containing the current input text. On save-and-quit, reads back the
updated text and applies it to the widget.
"""

from __future__ import annotations

import os
import tempfile
from typing import Any

from .protocols import EditorSuspender, FocusManager, WidgetDiscovery


class EditorLauncher:
    """Launches $EDITOR for the currently focused input widget.

    Flow:
        1. Read current text from focused input
        2. Write to temp file
        3. Suspend UI and run editor
        4. Read temp file back
        5. Update input widget text
        6. Clean up temp file
    """

    def __init__(
        self,
        focus_manager: FocusManager,
        widget_discovery: WidgetDiscovery,
        editor_suspender: EditorSuspender,
    ) -> None:
        self._focus = focus_manager
        self._discovery = widget_discovery
        self._suspender = editor_suspender

    def _get_editor(self) -> str:
        """Resolve the editor command from environment."""
        return os.environ.get("VISUAL") or os.environ.get("EDITOR", "vi")

    def launch(self) -> bool:
        """Open $EDITOR for the focused input widget.

        Returns True if the text was updated, False otherwise.
        """
        focused = self._focus.get_focused()
        if focused is None:
            return False

        if not self._focus.is_input_widget(focused):
            return False

        return self._edit_widget(focused)

    def _edit_widget(self, widget: Any) -> bool:
        """Edit a specific widget's text content via $EDITOR."""
        current_text = self._discovery.get_text_content(widget)
        editor = self._get_editor()

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".md", prefix="supyx_edit_")
        try:
            with os.fdopen(tmp_fd, "w") as f:
                f.write(current_text)

            exit_code = self._suspender.suspend_and_run([editor, tmp_path])

            if exit_code != 0:
                return False

            with open(tmp_path, "r") as f:
                new_text = f.read()

            # Only update if text actually changed
            if new_text != current_text:
                self._discovery.set_text_content(widget, new_text)
                return True

            return False
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
