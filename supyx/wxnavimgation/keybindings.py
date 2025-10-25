"""
Keybinding management system.
"""

import wx


class KeyBindingManager:
    """
    Manages keyboard shortcuts and command mappings.
    
    Allows mapping keys to functions with descriptions.
    """
    
    def __init__(self, parent):
        """
        Initialize the keybinding manager.
        
        Args:
            parent: The parent wx.Frame or window
        """
        self.parent = parent
        self.bindings = {}
        self.multi_key_buffer = []
        self.multi_key_timer = None
    
    def map_key(self, key_sequence, callback, description=""):
        """
        Map a key sequence to a callback function.
        
        Args:
            key_sequence: String like 'f', 'dd', 'gg', etc.
            callback: Function to call when key sequence is pressed
            description: Optional description of what the command does
        """
        self.bindings[key_sequence] = {
            'callback': callback,
            'description': description
        }
    
    def unmap_key(self, key_sequence):
        """Remove a key mapping."""
        if key_sequence in self.bindings:
            del self.bindings[key_sequence]
    
    def handle_key(self, key):
        """
        Handle a key press and check if it matches any bindings.
        
        Args:
            key: The key string
            
        Returns:
            True if the key was handled, False otherwise
        """
        # Add to buffer for multi-key sequences
        self.multi_key_buffer.append(key)
        current_sequence = ''.join(self.multi_key_buffer)
        
        # Reset timer
        if self.multi_key_timer:
            self.multi_key_timer.Stop()
        
        # Check for exact match
        if current_sequence in self.bindings:
            binding = self.bindings[current_sequence]
            self.multi_key_buffer = []
            wx.CallAfter(binding['callback'])
            return True
        
        # Check if this could be the start of a longer sequence
        possible_match = any(
            seq.startswith(current_sequence) and len(seq) > len(current_sequence)
            for seq in self.bindings.keys()
        )
        
        if possible_match:
            # Wait for next key
            self.multi_key_timer = wx.CallLater(1000, self._reset_buffer)
            return True
        
        # No match, reset buffer
        self.multi_key_buffer = []
        return False
    
    def _reset_buffer(self):
        """Reset the multi-key buffer after timeout."""
        self.multi_key_buffer = []
    
    def get_bindings(self):
        """Get all current key bindings."""
        return dict(self.bindings)
    
    def show_help(self):
        """Show a help dialog with all key bindings."""
        help_text = "Keyboard Shortcuts:\n\n"
        for key, binding in sorted(self.bindings.items()):
            desc = binding['description'] or "No description"
            help_text += f"{key:10} - {desc}\n"
        
        dlg = wx.MessageDialog(
            self.parent,
            help_text,
            "Keyboard Shortcuts",
            wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()

