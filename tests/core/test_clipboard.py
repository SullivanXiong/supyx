"""Tests for supyx.core.clipboard.ClipboardImageDetector."""

from __future__ import annotations

import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from supyx.core.clipboard import ClipboardImageDetector


class TestClipboardImageDetector:
    def test_whenNotMacOS_thenReturnsNone(self):
        detector = ClipboardImageDetector()
        with patch("supyx.core.clipboard.platform.system", return_value="Linux"):
            assert detector.save_image_to_temp() is None

    @patch("supyx.core.clipboard.platform.system", return_value="Darwin")
    @patch("supyx.core.clipboard.shutil.which", return_value="/usr/local/bin/pngpaste")
    @patch("supyx.core.clipboard.subprocess.run")
    def test_whenPngpasteSucceeds_thenReturnsTempPath(self, mock_run, mock_which, mock_system):
        mock_run.return_value = MagicMock(returncode=0)

        detector = ClipboardImageDetector()
        result = detector.save_image_to_temp()

        assert result is not None
        assert result.endswith(".png")
        assert "supyx_paste_" in result

        # Clean up
        if result and os.path.exists(result):
            os.unlink(result)

    @patch("supyx.core.clipboard.platform.system", return_value="Darwin")
    @patch("supyx.core.clipboard.shutil.which", return_value="/usr/local/bin/pngpaste")
    @patch("supyx.core.clipboard.subprocess.run")
    def test_whenPngpasteFails_thenReturnsNone(self, mock_run, mock_which, mock_system):
        mock_run.return_value = MagicMock(returncode=1)

        detector = ClipboardImageDetector()
        result = detector.save_image_to_temp()

        assert result is None

    @patch("supyx.core.clipboard.platform.system", return_value="Darwin")
    @patch("supyx.core.clipboard.shutil.which", return_value=None)
    @patch("supyx.core.clipboard.subprocess.run")
    def test_whenNoPngpaste_thenFallsBackToOsascript(self, mock_run, mock_which, mock_system):
        # First call: osascript clipboard check (returns image info)
        # Second call: osascript save (returns "ok")
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="«class PNGf», 12345"),
            MagicMock(returncode=0, stdout="ok"),
        ]

        detector = ClipboardImageDetector()
        result = detector.save_image_to_temp()

        assert result is not None
        assert result.endswith(".png")

        # Clean up
        if result and os.path.exists(result):
            os.unlink(result)

    @patch("supyx.core.clipboard.platform.system", return_value="Darwin")
    @patch("supyx.core.clipboard.shutil.which", return_value=None)
    @patch("supyx.core.clipboard.subprocess.run")
    def test_whenOsascriptNoImage_thenReturnsNone(self, mock_run, mock_which, mock_system):
        # osascript clipboard check returns text-only info (no image class)
        mock_run.return_value = MagicMock(returncode=0, stdout="«class utf8», 100")

        detector = ClipboardImageDetector()
        result = detector.save_image_to_temp()

        assert result is None

    @patch("supyx.core.clipboard.platform.system", return_value="Darwin")
    @patch("supyx.core.clipboard.shutil.which", return_value=None)
    @patch("supyx.core.clipboard.subprocess.run")
    def test_whenOsascriptSaveFails_thenReturnsNone(self, mock_run, mock_which, mock_system):
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="«class PNGf», 12345"),
            MagicMock(returncode=0, stdout="no_image"),
        ]

        detector = ClipboardImageDetector()
        result = detector.save_image_to_temp()

        assert result is None
