# supyx

Personal Python utilities library by suxiong.

## Packages

### wxNaVimgation

Vim-like navigation for wxPython applications, inspired by Surfingkeys browser extension.

Features:

- **Normal mode**: Default navigation mode with keyboard shortcuts
- **Insert mode**: For text input (activated with `i` or when focusing input fields)
- **Hint mode**: Press `f` to show hints on clickable elements, type hint to click
- **Search mode**: Press `/` to search text in the application
- **Quick navigation**: `i` to focus first input field, `gi` to cycle through inputs
- Extensible keybinding system for custom commands

## Installation

```bash
pip install supyx
```

Or with uv:

```bash
uv add supyx
```

## Usage

```python
import wx
from supyx.wxnavimgation import VimNavigationMixin

class MyFrame(VimNavigationMixin, wx.Frame):
    def __init__(self):
        super().__init__(None, title="My App")
        self.init_vim_navigation()

        # Add custom keybindings
        self.vim_nav.map_key('dd', self.delete_item, "Delete selected item")
```

## License

MIT
