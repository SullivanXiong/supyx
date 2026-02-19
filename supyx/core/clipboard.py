"""
OS-level clipboard image detection.

Checks if the system clipboard contains an image and saves it to a temp file.
Framework-agnostic — uses subprocess calls to OS tools (no wx/Textual deps).

macOS: prefers `pngpaste` (brew install pngpaste), falls back to osascript.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import tempfile
from typing import Optional


class ClipboardImageDetector:
    """Detects clipboard images and saves them to temp files.

    Supports macOS. Returns None on unsupported platforms or when
    no image is in the clipboard.
    """

    def save_image_to_temp(self) -> Optional[str]:
        """Check clipboard for an image and save to a temp file.

        Returns the temp file path if an image was found, None otherwise.
        The caller is responsible for cleaning up the temp file.
        """
        system = platform.system()
        if system == "Darwin":
            return self._macos_save()
        # Linux/Windows support can be added later
        return None

    def _macos_save(self) -> Optional[str]:
        """Save clipboard image on macOS."""
        # Prefer pngpaste — fast, purpose-built
        if shutil.which("pngpaste"):
            return self._try_pngpaste()
        # Fall back to osascript
        return self._try_osascript()

    def _try_pngpaste(self) -> Optional[str]:
        """Use pngpaste to save clipboard image."""
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".png", prefix="supyx_paste_")
        try:
            import os

            os.close(tmp_fd)
            result = subprocess.run(
                ["pngpaste", tmp_path],
                capture_output=True,
            )
            if result.returncode == 0:
                return tmp_path
            # pngpaste returns non-zero when clipboard has no image
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            return None
        except Exception:
            try:
                import os

                os.unlink(tmp_path)
            except OSError:
                pass
            return None

    def _try_osascript(self) -> Optional[str]:
        """Use osascript to check clipboard and save image via screencapture."""
        # First check if clipboard has an image
        check_script = (
            'tell application "System Events" to return '
            "(the clipboard info) as text"
        )
        try:
            result = subprocess.run(
                ["osascript", "-e", check_script],
                capture_output=True,
                text=True,
            )
            if "«class PNGf»" not in result.stdout and "TIFF" not in result.stdout:
                return None
        except Exception:
            return None

        # Save the image using osascript + write to file
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".png", prefix="supyx_paste_")
        try:
            import os

            os.close(tmp_fd)

            save_script = f"""
                set theFile to POSIX file "{tmp_path}"
                try
                    set theImage to the clipboard as «class PNGf»
                    set fileRef to open for access theFile with write permission
                    write theImage to fileRef
                    close access fileRef
                    return "ok"
                on error
                    return "no_image"
                end try
            """
            result = subprocess.run(
                ["osascript", "-e", save_script],
                capture_output=True,
                text=True,
            )
            if "ok" in result.stdout:
                return tmp_path

            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            return None
        except Exception:
            try:
                import os

                os.unlink(tmp_path)
            except OSError:
                pass
            return None
