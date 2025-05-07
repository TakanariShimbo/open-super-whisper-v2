"""
Hotkey Manager Implementation

This module provides a platform-independent implementation for registering and managing global hotkeys.
"""

# Standard library imports
from typing import Callable, Optional, List, Sequence, Dict

# Third-party imports
from pynput import keyboard


class HotkeyManager:
    """
    Implementation for managing global hotkeys.
    
    This class provides methods to register and unregister global hotkeys
    that can be triggered even when the application is not in focus.
    Uses pynput library for the actual keyboard monitoring.
    
    Examples
    --------
    Basic usage:
    
    >>> hotkey_manager = HotkeyManager()
    >>> # Register a hotkey for Ctrl+Shift+R
    >>> hotkey_manager.register_hotkey("ctrl+shift+r", lambda: print("Hotkey pressed!"))
    >>> # Unregister the hotkey when no longer needed
    >>> hotkey_manager.unregister_hotkey("ctrl+shift+r")
    
    Filtered mode example:
    
    >>> hotkey_manager = HotkeyManager()
    >>> # Register multiple hotkeys
    >>> hotkey_manager.register_hotkey("ctrl+shift+r", lambda: print("Action R"))
    >>> hotkey_manager.register_hotkey("ctrl+shift+s", lambda: print("Action S"))
    >>> # Enable filtered mode to only allow specific hotkey
    >>> hotkey_manager.enable_filtered_mode(["ctrl+shift+r"])
    >>> # Later, disable filtered mode to restore all hotkeys
    >>> hotkey_manager.disable_filtered_mode()
    """
    
    # Class constants for key mappings
    MODIFIER_KEYS: Dict[str, str] = {
        'ctrl': '<ctrl>',
        'control': '<ctrl>',
        'alt': '<alt>',
        'option': '<alt>',  # for macOS
        'shift': '<shift>',
        'cmd': '<cmd>',
        'command': '<cmd>',
        'win': '<cmd>',
        'windows': '<cmd>',
        'meta': '<cmd>'
    }
    
    SPECIAL_KEYS: Dict[str, str] = {
        'f1': '<f1>', 'f2': '<f2>', 'f3': '<f3>', 'f4': '<f4>',
        'f5': '<f5>', 'f6': '<f6>', 'f7': '<f7>', 'f8': '<f8>',
        'f9': '<f9>', 'f10': '<f10>', 'f11': '<f11>', 'f12': '<f12>',
        'esc': '<esc>', 'escape': '<esc>',
        'tab': '<tab>',
        'space': '<space>',
        'backspace': '<backspace>', 'bs': '<backspace>',
        'enter': '<enter>', 'return': '<enter>',
        'ins': '<insert>', 'insert': '<insert>',
        'del': '<delete>', 'delete': '<delete>',
        'home': '<home>',
        'end': '<end>',
        'pageup': '<page_up>', 'pgup': '<page_up>',
        'pagedown': '<page_down>', 'pgdn': '<page_down>',
        'up': '<up>', 'down': '<down>', 'left': '<left>', 'right': '<right>',
        'capslock': '<caps_lock>', 'caps': '<caps_lock>',
        'numlock': '<num_lock>', 'num': '<num_lock>',
        'scrolllock': '<scroll_lock>', 'scrl': '<scroll_lock>',
        'prtsc': '<print_screen>', 'printscreen': '<print_screen>'
    }
    
    def __init__(self):
        """
        Initialize the HotkeyManager.
        """
        self._hotkeys: Dict[str, Callable] = {}  # Dictionary to store hotkey strings and their callbacks
        self._listener: Optional[keyboard.GlobalHotKeys] = None  # Will be set to a listener object when active
        self._active_hotkeys: Optional[List[str]] = None  # None = filter mode off, list = filter mode on (even empty list)
    
    @property
    def is_listening(self) -> bool:
        """
        Check if the hotkey manager is currently listening for hotkeys.
        
        Returns
        -------
        bool
            True if the manager is actively listening, False otherwise.
        """
        return self._listener is not None
        
    @property
    def is_filter_mode_active(self) -> bool:
        """
        Check if the hotkey manager is in filtered mode.
        
        Returns
        -------
        bool
            True if filter mode is active, False otherwise.
        """
        return self._active_hotkeys is not None
    
    def register_hotkey(self, hotkey_string: str, callback: Callable) -> None:
        """
        Register a global hotkey.
        
        Parameters
        ----------
        hotkey_string : str
            String representation of the hotkey (e.g., "ctrl+shift+r").
        callback : Callable
            Function to call when the hotkey is pressed.
            
        Returns
        -------
        None
        
        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        ValueError
            If the hotkey string is invalid.
        """
        # Only allow registration if not listening
        if self.is_listening:
            raise RuntimeError("Cannot register hotkey: listener is active. Stop listening first.")
            
        # Parse hotkey string into the format pynput expects
        hotkey_combination = self.parse_hotkey_string(hotkey_string)
        if not hotkey_combination:
            raise ValueError(f"Invalid hotkey string: {hotkey_string}")
        
        # Add the hotkey to our dictionary
        self._hotkeys[hotkey_combination] = callback
    
    def unregister_hotkey(self, hotkey_string: str) -> bool:
        """
        Unregister a previously registered global hotkey.
        
        Parameters
        ----------
        hotkey_string : str
            String representation of the hotkey to unregister.
            
        Returns
        -------
        bool
            True if the hotkey was successfully unregistered, False if it was not registered.
        
        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        ValueError
            If the hotkey string is invalid.
        """
        # Only allow unregistration if not listening
        if self.is_listening:
            raise RuntimeError("Cannot unregister hotkey: listener is active. Stop listening first.")
            
        # Parse hotkey string
        hotkey_combination = self.parse_hotkey_string(hotkey_string)
        
        # Check if hotkey string is valid
        if not hotkey_combination:
            raise ValueError(f"Invalid hotkey string: {hotkey_string}")
        
        # Check if hotkey is registered
        if hotkey_combination not in self._hotkeys:
            return False
        
        # Remove hotkey from dictionary
        del self._hotkeys[hotkey_combination]
        return True
    
    def enable_filtered_mode(self, active_hotkeys: Sequence[str]) -> None:
        """
        Enable filtered mode to allow only specific hotkeys to work.
        
        When filtered mode is enabled, only the specified hotkeys will trigger callbacks.
        All other hotkeys will be ignored.
        
        Parameters
        ----------
        active_hotkeys : Sequence[str]
            Sequence of hotkey strings that should remain active when filtered mode is enabled.
            Must not be empty.
            
        Returns
        -------
        None
        
        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        ValueError
            If the hotkey string is invalid.
        """
        # Only allow mode change if not listening
        if self.is_listening:
            raise RuntimeError("Cannot enable filtered mode: listener is active. Stop listening first.")
        
        # Create a temporary list for parsed hotkeys
        parsed_hotkeys = []
        
        # Parse and validate each active hotkey
        for hotkey in active_hotkeys:
            parsed_hotkey = self.parse_hotkey_string(hotkey)
            if not parsed_hotkey:
                raise ValueError(f"Invalid hotkey string: {hotkey}")
            parsed_hotkeys.append(parsed_hotkey)
        
        # All hotkeys are valid, now set the active hotkeys list
        self._active_hotkeys = parsed_hotkeys
                
    def disable_filtered_mode(self) -> None:
        """
        Disable filtered mode and allow all registered hotkeys to work.
        
        Returns
        -------
        None
        
        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        """
        # Only allow mode change if not listening
        if self.is_listening:
            raise RuntimeError("Cannot disable filtered mode: listener is active. Stop listening first.")
        
        # Set to None to indicate filter mode is inactive
        self._active_hotkeys = None
    
    def start_listening(self) -> None:
        """
        Start the hotkey listener.
        
        Returns
        -------
        None
        
        Raises
        ------
        RuntimeError
            If there are no hotkeys registered or if the listener is already active.
        """
        # Only start if we have hotkeys to listen for
        if not self._hotkeys:
            raise RuntimeError("Cannot start listening: no hotkeys registered")
            
        if self.is_listening:
            raise RuntimeError("Listener is already active")
        
        # Create and start a listener with our hotkeys and event filtering
        if self.is_filter_mode_active:
            self._start_filtered_listening()
        else:
            self._start_normal_listening()
        
        self._listener.start()
    
    def _start_filtered_listening(self) -> None:
        """
        Start listening with filtered mode active.

        Only the active hotkeys will be monitored.
        """
        # Create filtered hotkeys using dictionary comprehension
        filtered_hotkeys = {
            hotkey: callback 
            for hotkey, callback in self._hotkeys.items() 
            if hotkey in self._active_hotkeys
        }
        
        # Filtered mode, use only active hotkeys
        self._listener = keyboard.GlobalHotKeys(filtered_hotkeys)
    
    def _start_normal_listening(self) -> None:
        """
        Start listening in normal mode.
        
        All registered hotkeys will be monitored.
        """
        # Normal mode, use all hotkeys
        self._listener = keyboard.GlobalHotKeys(self._hotkeys)
    
    def stop_listening(self) -> bool:
        """
        Stop the hotkey listener.
        
        This method stops the listener without unregistering the hotkeys.
        
        Returns
        -------
        bool
            True if the listener was stopped, False if there was no active listener.
        """
        if not self.is_listening:
            return False
        
        self._listener.stop()
        self._listener = None
        return True
    
    def clear_all_hotkeys(self) -> None:
        """
        Clear all registered hotkeys.
        
        Returns
        -------
        None
        
        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first.
        """
        # Only allow clearing if not listening
        if self.is_listening:
            raise RuntimeError("Cannot clear hotkeys: listener is active. Stop listening first.")
        
        # Clear the hotkeys dictionary
        self._hotkeys.clear()
    
    @classmethod
    def parse_hotkey_string(cls, hotkey_string: str) -> Optional[str]:
        """
        Convert a user-friendly hotkey string to the format pynput expects.
        
        Parameters
        ----------
        hotkey_string : str
            User-friendly hotkey string (e.g., "ctrl+shift+r").
            
        Returns
        -------
        Optional[str]
            Pynput format hotkey string (e.g., "<ctrl>+<shift>+r"), or None if invalid.
            
        Examples
        --------
        >>> HotkeyManager.parse_hotkey_string("ctrl+shift+r")
        '<ctrl>+<shift>+r'
        >>> HotkeyManager.parse_hotkey_string("alt+f4")
        '<alt>+<f4>'
        >>> HotkeyManager.parse_hotkey_string("command+option+space")
        '<cmd>+<alt>+<space>'
        >>> HotkeyManager.parse_hotkey_string("")
        None
        """
        if not hotkey_string:
            return None
        
        # Normalize to lowercase and split by '+'
        parts = [part.strip() for part in hotkey_string.lower().split('+')]
        
        # Ensure we have valid parts
        if not parts:
            return None
            
        processed_parts = []
        
        for part in parts:
            # Skip empty parts
            if not part:
                continue
                
            # Check for modifier keys first
            if part in cls.MODIFIER_KEYS:
                processed_parts.append(cls.MODIFIER_KEYS[part])
            # Then check for special keys
            elif part in cls.SPECIAL_KEYS:
                processed_parts.append(cls.SPECIAL_KEYS[part])
            # Single character keys (a-z, 0-9, etc.)
            elif len(part) == 1:
                processed_parts.append(part)
            # Unknown part - pass it through as-is with a warning comment
            else:
                processed_parts.append(part)
        
        # Return None if no valid parts were found
        if not processed_parts:
            return None
            
        # Join all parts with '+' to create the final hotkey string
        return '+'.join(processed_parts)
