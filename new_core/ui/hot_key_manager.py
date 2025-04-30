"""
Hotkey Manager Implementation

This module provides a platform-independent implementation for registering and managing global hotkeys.
"""

from typing import Callable, Optional
from pynput import keyboard


class HotKeyManager:
    """
    Implementation for managing global hotkeys.
    
    This class provides methods to register and unregister global hotkeys
    that can be triggered even when the application is not in focus.
    Uses pynput library for the actual keyboard monitoring.
    
    Examples
    --------
    Basic usage:
    
    >>> hotkey_manager = HotKeyManager()
    >>> # Register a hotkey for Ctrl+Shift+R
    >>> hotkey_manager.register_hotkey("ctrl+shift+r", lambda: print("Hotkey pressed!"))
    >>> # Unregister the hotkey when no longer needed
    >>> hotkey_manager.unregister_hotkey("ctrl+shift+r")
    
    Recording mode example:
    
    >>> hotkey_manager = HotKeyManager()
    >>> # Register multiple hotkeys
    >>> hotkey_manager.register_hotkey("ctrl+shift+r", lambda: print("Recording started"))
    >>> hotkey_manager.register_hotkey("ctrl+shift+s", lambda: print("Normal action"))
    >>> # Enter recording mode, where only the specified hotkey works
    >>> hotkey_manager.enable_recording_mode(True, "ctrl+shift+r")
    >>> # Later, disable recording mode to restore all hotkeys
    >>> hotkey_manager.enable_recording_mode(False)
    """
    
    def __init__(self):
        """
        Initialize the HotKeyManager.
        """
        self._is_listener_active = False
        self._hotkeys = {}  # Dictionary to store hotkey strings and their callbacks
        self._listener = None
        self._is_recording_active = False  # Flag to indicate if recording is in progress
        self._active_recording_hotkey = None  # Store the recording hotkey for filtering
    
    def register_hotkey(self, hotkey_string: str, callback: Callable) -> bool:
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
        bool
            True if registration was successful, False otherwise.
        """
        # Stop existing listener if it's running
        self.stop_listening()
        
        # Parse hotkey string into the format pynput expects
        hotkey_combination = self.parse_hotkey_string(hotkey_string)
        if not hotkey_combination:
            return False
        
        # Add the hotkey to our dictionary
        self._hotkeys[hotkey_combination] = callback
        
        # Start the listener with the updated hotkeys
        return self.start_listening()
    
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
            True if unregistration was successful, False otherwise.
        """
        # Parse hotkey string
        hotkey_combination = self.parse_hotkey_string(hotkey_string)
        
        # Check if hotkey is registered
        if not hotkey_combination or hotkey_combination not in self._hotkeys:
            return False
        
        # Stop listener
        self.stop_listening()
        
        # Remove hotkey from dictionary
        del self._hotkeys[hotkey_combination]
        
        # Restart listener if there are still hotkeys registered
        if self._hotkeys:
            return self.start_listening()
            
        return True
    
    def enable_recording_mode(self, enabled: bool, recording_hotkey: Optional[str] = None) -> None:
        """
        Enable or disable recording mode to filter hotkey events.
        
        When recording mode is enabled, only the specified recording hotkey will trigger a callback.
        All other hotkeys will be ignored. If recording_hotkey is None and enabled is True, 
        all hotkeys will be disabled.
        
        Parameters
        ----------
        enabled : bool
            Whether to enable recording mode.
        recording_hotkey : Optional[str]
            The hotkey string used for recording. This hotkey will still work
            even when recording mode is enabled.
        """
        # Store previous state for restart check
        prev_recording_mode = self._is_recording_active
        
        self._is_recording_active = enabled
        
        if enabled and recording_hotkey:
            # Parse and store the recording hotkey for filtering
            self._active_recording_hotkey = self.parse_hotkey_string(recording_hotkey)
        else:
            # Reset recording hotkey when disabled
            self._active_recording_hotkey = None
        
        # If listener is active and recording mode changed, restart the listener to apply the changes
        if self._is_listener_active and prev_recording_mode != self._is_recording_active:
            self.stop_listening()
            self.start_listening()
    
    def start_listening(self) -> bool:
        """
        Start the hotkey listener.
        
        Returns
        -------
        bool
            True if the listener was started successfully.
        """
        # Only start if we have hotkeys to listen for
        if not self._hotkeys:
            return False
        
        # Create and start a listener with our hotkeys and event filtering
        if self._is_recording_active:
            # In recording mode, we need to create a custom listener that filters events
            filtered_hotkeys = {}
            
            if self._active_recording_hotkey:
                # Only include the recording hotkey if specified
                for hotkey, callback in self._hotkeys.items():
                    if hotkey == self._active_recording_hotkey:
                        filtered_hotkeys[hotkey] = callback
                
                # Use filtered hotkeys if we're in recording mode
                if filtered_hotkeys:
                    self._listener = keyboard.GlobalHotKeys(filtered_hotkeys)
                else:
                    # If recording hotkey not found, use no hotkeys to effectively disable all
                    self._listener = keyboard.GlobalHotKeys({})
            else:
                # If active_recording_hotkey is None in recording mode, disable all hotkeys
                self._listener = keyboard.GlobalHotKeys({})
        else:
            # Normal mode, use all hotkeys
            self._listener = keyboard.GlobalHotKeys(self._hotkeys)
        
        self._listener.start()
        self._is_listener_active = True
        
        return True
    
    def stop_listening(self) -> bool:
        """
        Stop the hotkey listener.
        
        This method stops the listener without unregistering the hotkeys.
        
        Returns
        -------
        bool
            True if the listener was stopped successfully.
        """
        if self._listener and self._is_listener_active:
            self._listener.stop()
            self._listener = None
            self._is_listener_active = False
            return True
        
        return False
    
    def clear_all_hotkeys(self) -> bool:
        """
        Clear all registered hotkeys.
        
        Returns
        -------
        bool
            True if all hotkeys were cleared successfully.
        """
        # Stop the listener
        self.stop_listening()
        
        # Clear the hotkeys dictionary
        self._hotkeys.clear()
        
        return True
    
    @staticmethod
    def parse_hotkey_string(hotkey_string: str) -> Optional[str]:
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
        """
        if not hotkey_string:
            return None
        
        # Normalize to lowercase
        hotkey_string = hotkey_string.lower()
        
        # Define mappings for modifier keys
        modifier_mapping = {
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
        
        # Define mappings for special keys
        special_key_mapping = {
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
        
        # Split the hotkey string by '+' and process each part
        parts = hotkey_string.split('+')
        processed_parts = []
        
        for part in parts:
            part = part.strip()
            
            if part in modifier_mapping:
                processed_parts.append(modifier_mapping[part])
            elif part in special_key_mapping:
                processed_parts.append(special_key_mapping[part])
            elif len(part) == 1:  # Single character keys
                processed_parts.append(part)
            else:
                processed_parts.append(part)
        
        # Return None if no valid parts were found
        if not processed_parts:
            return None
            
        # Join all parts with '+' to create the final hotkey string
        return '+'.join(processed_parts)