"""
Core types used throughout supyx.

No framework imports — pure Python dataclasses and enums.
"""

from __future__ import annotations

import dataclasses
from enum import Enum


class VimMode(Enum):
    """Navigation modes for the application."""

    DEFAULT = "DEFAULT"  # Normal state, no overlay active
    HINT = "HINT"  # Hint overlay active
    SEARCH = "SEARCH"  # Search overlay active


@dataclasses.dataclass(frozen=True)
class KeyEvent:
    """Framework-agnostic representation of a key press.

    Each backend converts its native key event into this format
    before passing to the core ModeStateMachine.
    """

    key_string: str  # normalized: "a", "escape", "return", "/", etc.
    raw_keycode: int = 0  # original keycode from the framework
    ctrl: bool = False
    alt: bool = False
    shift: bool = False
