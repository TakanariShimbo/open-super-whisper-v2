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
    information about currently pressed keys and the last key combination.
    
    Examples
    --------
    Basic usage:
    
    >>> key_state_tracker = KeyStateTracker()
    >>> # Start monitoring keyboard input
    >>> key_state_tracker.start()
    >>> # Get the current pressed keys as a string
    >>> current_keys = key_state_tracker.get_current_keys_str()
    >>> print(f"Current pressed keys: {current_keys}")
    >>> # Get the last pressed key combination as a string
    >>> last_keys = key_state_tracker.get_keys_str()
    >>> print(f"Last key combination: {last_keys}")
    >>> # Stop monitoring keyboard input
    >>> key_state_tracker.stop()
    """
    
    def __init__(self):
        """
        Initialize the KeyStateTracker.
        """
        self._listener: keyboard.Listener | None = None
        self._pressed_keys: set[keyboard.Key | keyboard.KeyCode] = set()  # Set of currently pressed keys
        self._last_keys: set[keyboard.Key | keyboard.KeyCode] = set()  # Set of last pressed key combination
    
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
        self._last_keys.clear()
        
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
        self._last_keys.clear()
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

        has_new_key = False
        for key in self._pressed_keys:
            if key in self._last_keys:
                continue
            else:
                has_new_key = True
                print("new key: ", key)
                break

        if has_new_key:
            self._last_keys = self._pressed_keys.copy()

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
    
    def _format_keys_to_str(self, keys: set[keyboard.Key | keyboard.KeyCode]) -> str:
        """
        Format a set of keys into a sorted string representation.
        
        Parameters
        ----------
        keys : set[keyboard.Key | keyboard.KeyCode]
            Set of keys to format
            
        Returns
        -------
        str
            A string containing all keys formatted and sorted (modifiers first),
            separated by '+'. Empty string if no keys are provided.
        """
        if not keys:
            return ""
            
        # Convert all keys to strings
        key_strings = [KeyFormatter.format_key(key) for key in keys]
        
        # Separate modifiers and regular keys
        modifier_keys = []
        regular_keys = []
        
        # List of all modifier key names
        modifiers = ('ctrl', 'ctrl_l', 'ctrl_r', 'alt', 'alt_l', 'alt_r', 
                    'shift', 'shift_l', 'shift_r', 'cmd', 'cmd_l', 'cmd_r')
        
        for key_str in key_strings:
            if key_str in modifiers:
                modifier_keys.append(key_str)
            else:
                regular_keys.append(key_str)
                
        # Sort both lists
        modifier_keys.sort()
        regular_keys.sort()
        
        # Combine with modifiers first
        sorted_keys = modifier_keys + regular_keys
        
        # Join with '+' and return
        return '+'.join(sorted_keys) if sorted_keys else ""
    
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
            
        return self._format_keys_to_str(self._pressed_keys)
        
    def get_last_keys_str(self) -> str:
        """
        Get a string representation of the last pressed key combination.

        Returns
        -------
        str
            A string containing the last pressed key combination, separated by '+'.
            Empty string if no keys have been pressed or monitoring is not active.
        """
        if not self.is_monitoring:
            return ""
            
        return self._format_keys_to_str(self._last_keys)
