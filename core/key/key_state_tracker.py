"""
Key State Tracker Implementation

This module provides functionality for monitoring keyboard inputs
and tracking key press history.
"""

from pynput import keyboard

from .key_formatter import KeyFormatter


class KeyStateTracker:
    """
    Implementation for monitoring keyboard inputs.

    This class provides methods to track keyboard inputs and retrieve
    information about currently pressed keys.
    
    Examples
    --------
    Basic usage:
    
    >>> key_state_tracker = KeyStateTracker()
    >>> # Start monitoring keyboard input
    >>> key_state_tracker.start()
    >>> # Get the current pressed keys as a string
    >>> current_keys = key_state_tracker.get_current_keys_str()
    >>> print(f"Current pressed keys: {current_keys}")
    >>> # Stop monitoring keyboard input
    >>> key_state_tracker.stop()
    """
    
    def __init__(self):
        """
        Initialize the KeyStateTracker.
        """
        self._listener: keyboard.Listener | None = None
        self._pressed_keys: set[keyboard.Key | keyboard.KeyCode] = set()  # Set of currently pressed keys
    
    @property
    def is_monitoring(self) -> bool:
        """
        Check if keyboard input monitoring is active.
        
        Returns
        -------
        bool
            True if keyboard monitoring is active, False otherwise.
        """
        return self._listener is not None and self._listener.running
    
    def start(self) -> None:
        """
        Start monitoring all keyboard inputs.
        
        This method starts a keyboard listener that tracks all key presses and releases.
        
        Returns
        -------
        None
        
        Raises
        ------
        RuntimeError
            If the key monitor is already active.
        """
        if self.is_monitoring:
            raise RuntimeError("Key monitor is already active")
        
        # Clear any previously stored keys
        self._pressed_keys.clear()
        
        # Create and start the keyboard listener
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._listener.start()
    
    def stop(self) -> bool:
        """
        Stop monitoring keyboard inputs.
        
        Returns
        -------
        bool
            True if the key monitor was stopped, False if there was no active key monitor.
        """
        if not self.is_monitoring:
            return False
            
        self._listener.stop()
        self._listener = None
        self._pressed_keys.clear()
        return True
    
    def _on_key_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """
        Handle key press events.
        
        Parameters
        ----------
        key : pynput.keyboard.Key or pynput.keyboard.KeyCode
            The key that was pressed.
        """
        # Add the key to the set of pressed keys
        self._pressed_keys.add(key)
            
    def _on_key_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        """
        Handle key release events.
        
        Parameters
        ----------
        key : pynput.keyboard.Key or pynput.keyboard.KeyCode
            The key that was released.
        """
        # Remove the key from the set of pressed keys
        self._pressed_keys.discard(key)
    
    def get_current_keys_str(self) -> str:
        """
        Get a string representation of all currently pressed keys.
        
        Returns
        -------
        str
            A string containing all currently pressed keys, separated by '+'.
            Empty string if no keys are pressed or monitoring is not active.
        """
        if not self.is_monitoring:
            return ""
            
        # Convert all pressed keys to strings and sort them
        key_strings = [KeyFormatter.format_key(key) for key in self._pressed_keys]
        
        # Put modifier keys first
        modifier_first = []
        regular_keys = []
        
        for key_str in key_strings:
            if key_str in ('ctrl', 'ctrl_l', 'ctrl_r', 'alt', 'alt_l', 'alt_r', 
                          'shift', 'shift_l', 'shift_r', 'cmd', 'cmd_l', 'cmd_r'):
                modifier_first.append(key_str)
            else:
                regular_keys.append(key_str)
                
        # Sort modifiers and regular keys separately
        modifier_first.sort()
        regular_keys.sort()
        
        # Combine the sorted lists
        sorted_keys = modifier_first + regular_keys
        
        # Join with '+' and return
        return '+'.join(sorted_keys) if sorted_keys else ""
