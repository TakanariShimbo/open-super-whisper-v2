"""
Hotkey Manager Interface

This module provides an interface for registering and managing global hotkeys.
"""

from typing import Callable


class HotkeyManager:
    """
    Interface for managing global hotkeys.
    
    This class provides methods to register and unregister global hotkeys
    that can be triggered even when the application is not in focus.
    The actual hotkey implementation will be added later.
    """
    
    def __init__(self):
        """
        Initialize the HotkeyManager.
        """
        self._listener_active = False
        self._current_hotkey = None
        self._callback = None
    
    def register_hotkey(self, hotkey_str: str, callback: Callable) -> bool:
        """
        Register a global hotkey.
        
        Parameters
        ----------
        hotkey_str : str
            String representation of the hotkey (e.g., "ctrl+shift+r").
        callback : Callable
            Function to call when the hotkey is pressed.
            
        Returns
        -------
        bool
            True if registration was successful, False otherwise.
        """
        # Store the callback and hotkey
        self._current_hotkey = hotkey_str
        self._callback = callback
        
        # Start the listener
        self._listener_active = True
        
        # Placeholder for actual implementation
        print(f"Registered hotkey: {hotkey_str}")
        
        return True
    
    def unregister_hotkey(self, hotkey_str: str) -> bool:
        """
        Unregister a previously registered global hotkey.
        
        Parameters
        ----------
        hotkey_str : str
            String representation of the hotkey to unregister.
            
        Returns
        -------
        bool
            True if unregistration was successful, False otherwise.
        """
        if self._current_hotkey != hotkey_str:
            return False
        
        # Reset the callback and hotkey
        self._current_hotkey = None
        self._callback = None
        
        # Stop the listener
        self._listener_active = False
        
        # Placeholder for actual implementation
        print(f"Unregistered hotkey: {hotkey_str}")
        
        return True
    
    def stop_listener(self) -> None:
        """
        Stop the hotkey listener.
        
        This method stops the listener without unregistering the hotkey.
        """
        if not self._listener_active:
            return
        
        # Stop the listener
        self._listener_active = False
        
        # Placeholder for actual implementation
        print("Stopped hotkey listener")
    
    def restart_listener(self) -> None:
        """
        Restart the hotkey listener.
        
        This method restarts the listener if it was previously stopped.
        """
        if self._listener_active or not self._current_hotkey:
            return
        
        # Start the listener
        self._listener_active = True
        
        # Placeholder for actual implementation
        print("Restarted hotkey listener")
