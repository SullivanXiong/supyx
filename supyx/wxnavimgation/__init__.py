"""
wxNaVimgation - Vim-like navigation for wxPython applications.

Backward compatibility shim. For new code, use supyx.backends.wx directly.

Inspired by Surfingkeys browser extension.
"""

from supyx.backends.wx import WxVimNavigationMixin as VimNavigationMixin
from supyx.core.hints import HintController as HintOverlay
from supyx.core.keybindings import KeyBindingEngine as KeyBindingManager
from supyx.core.navigation import NavigationState as NavigationHelper
from supyx.core.search import SearchController as SearchOverlay
from supyx.core.types import VimMode

__all__ = [
    "VimMode",
    "VimNavigationMixin",
    "KeyBindingManager",
    "HintOverlay",
    "SearchOverlay",
    "NavigationHelper",
]
