"""Tests for supyx.core.editor.EditorLauncher."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from supyx.core.editor import EditorLauncher


class FakeFocusManager:
    def __init__(self, focused=None, is_input=True):
        self._focused = focused
        self._is_input = is_input

    def get_focused(self):
        return self._focused

    def set_focus(self, widget):
        self._focused = widget

    def is_input_widget(self, widget):
        return self._is_input

    def find_non_input_focusable(self):
        return None


class FakeWidgetDiscovery:
    def __init__(self):
        self._texts: dict = {}

    def find_widgets(self, widget_filter):
        return []

    def get_text_content(self, widget):
        return self._texts.get(id(widget), "")

    def set_text_content(self, widget, text):
        self._texts[id(widget)] = text


class FakeEditorSuspender:
    def __init__(self, exit_code=0, editor_fn=None):
        self._exit_code = exit_code
        self._editor_fn = editor_fn
        self.last_command = None

    def suspend_and_run(self, command):
        self.last_command = command
        if self._editor_fn:
            self._editor_fn(command)
        return self._exit_code


class TestEditorLauncher:
    def test_whenNoFocusedWidget_thenReturnsFalse(self):
        focus = FakeFocusManager(focused=None)
        discovery = FakeWidgetDiscovery()
        suspender = FakeEditorSuspender()

        launcher = EditorLauncher(focus, discovery, suspender)
        assert launcher.launch() is False

    def test_whenFocusedWidgetIsNotInput_thenReturnsFalse(self):
        widget = MagicMock()
        focus = FakeFocusManager(focused=widget, is_input=False)
        discovery = FakeWidgetDiscovery()
        suspender = FakeEditorSuspender()

        launcher = EditorLauncher(focus, discovery, suspender)
        assert launcher.launch() is False

    def test_whenEditorExitsNonZero_thenReturnsFalse(self):
        widget = MagicMock()
        focus = FakeFocusManager(focused=widget, is_input=True)
        discovery = FakeWidgetDiscovery()
        suspender = FakeEditorSuspender(exit_code=1)

        launcher = EditorLauncher(focus, discovery, suspender)
        assert launcher.launch() is False

    def test_whenEditorModifiesText_thenWidgetUpdated(self):
        widget = MagicMock()
        focus = FakeFocusManager(focused=widget, is_input=True)
        discovery = FakeWidgetDiscovery()
        discovery._texts[id(widget)] = "original text"

        def simulate_edit(command):
            # Write new text to the temp file (command[1] is the path)
            with open(command[1], "w") as f:
                f.write("edited text")

        suspender = FakeEditorSuspender(exit_code=0, editor_fn=simulate_edit)

        launcher = EditorLauncher(focus, discovery, suspender)
        result = launcher.launch()

        assert result is True
        assert discovery._texts[id(widget)] == "edited text"

    def test_whenEditorDoesNotModifyText_thenReturnsFalse(self):
        widget = MagicMock()
        focus = FakeFocusManager(focused=widget, is_input=True)
        discovery = FakeWidgetDiscovery()
        discovery._texts[id(widget)] = "same text"

        def dont_edit(command):
            pass  # Editor opens and quits without changes

        suspender = FakeEditorSuspender(exit_code=0, editor_fn=dont_edit)

        launcher = EditorLauncher(focus, discovery, suspender)
        result = launcher.launch()

        assert result is False
        assert discovery._texts[id(widget)] == "same text"

    def test_whenEditorCommand_thenUsesVisualEnv(self):
        widget = MagicMock()
        focus = FakeFocusManager(focused=widget, is_input=True)
        discovery = FakeWidgetDiscovery()
        suspender = FakeEditorSuspender(exit_code=1)

        launcher = EditorLauncher(focus, discovery, suspender)

        with patch.dict(os.environ, {"VISUAL": "code", "EDITOR": "nano"}):
            launcher.launch()

        assert suspender.last_command[0] == "code"

    def test_whenEditorCommand_thenFallsBackToEditorEnv(self):
        widget = MagicMock()
        focus = FakeFocusManager(focused=widget, is_input=True)
        discovery = FakeWidgetDiscovery()
        suspender = FakeEditorSuspender(exit_code=1)

        launcher = EditorLauncher(focus, discovery, suspender)

        with patch.dict(os.environ, {"EDITOR": "nano"}, clear=False):
            env = os.environ.copy()
            env.pop("VISUAL", None)
            with patch.dict(os.environ, env, clear=True):
                launcher.launch()

        assert suspender.last_command[0] == "nano"

    def test_whenNoEditorEnv_thenDefaultsToVi(self):
        widget = MagicMock()
        focus = FakeFocusManager(focused=widget, is_input=True)
        discovery = FakeWidgetDiscovery()
        suspender = FakeEditorSuspender(exit_code=1)

        launcher = EditorLauncher(focus, discovery, suspender)

        env = os.environ.copy()
        env.pop("VISUAL", None)
        env.pop("EDITOR", None)
        with patch.dict(os.environ, env, clear=True):
            launcher.launch()

        assert suspender.last_command[0] == "vi"

    def test_whenLaunchCompletes_thenTempFileCleanedUp(self):
        widget = MagicMock()
        focus = FakeFocusManager(focused=widget, is_input=True)
        discovery = FakeWidgetDiscovery()

        captured_path = []

        def capture_path(command):
            captured_path.append(command[1])

        suspender = FakeEditorSuspender(exit_code=0, editor_fn=capture_path)

        launcher = EditorLauncher(focus, discovery, suspender)
        launcher.launch()

        # Temp file should be cleaned up
        assert len(captured_path) == 1
        assert not os.path.exists(captured_path[0])
