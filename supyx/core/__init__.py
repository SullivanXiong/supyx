"""
supyx.core - Framework-agnostic vim navigation core.

Zero framework imports. All UI-specific behavior is delegated
to backends via Protocol-based contracts.
"""

from .clipboard import ClipboardImageDetector
from .editor import EditorLauncher
from .types import KeyEvent, VimMode

__all__ = [
    "ClipboardImageDetector",
    "EditorLauncher",
    "KeyEvent",
    "VimMode",
]
