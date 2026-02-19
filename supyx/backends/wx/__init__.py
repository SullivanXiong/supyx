"""
supyx.backends.wx - wxPython backend for vim navigation.

Requires: wxPython >= 4.2.0 (install via supyx[wx])
"""

from .mixin import WxVimNavigationMixin

__all__ = [
    "WxVimNavigationMixin",
]
