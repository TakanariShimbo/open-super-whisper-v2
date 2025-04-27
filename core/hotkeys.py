"""
Hotkey Manager Implementation

This module provides a platform-independent implementation for registering and managing global hotkeys.
"""

from typing import Callable, Dict, Optional, Set
from pynput import keyboard


class HotkeyManager:
    """
    Implementation for managing global hotkeys.
    
    This class provides methods to register and unregister global hotkeys
    that can be triggered even when the application is not in focus.
    Uses pynput library for the actual keyboard monitoring.
    """
    
    def __init__(self):
        """
        Initialize the HotkeyManager.
        """
        self._listener_active = False
        self._hotkeys = {}  # Dictionary to store hotkey strings and their callbacks
        self._listener = None
        self._recording_mode = False  # Flag to indicate if recording is in progress
        self._recording_hotkey = None  # Store the recording hotkey for filtering
    
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
        try:
            # Stop existing listener if it's running
            self.stop_listener()
            
            # Parse hotkey string into the format pynput expects
            hotkey_combination = self.parse_hotkey_string(hotkey_str)
            if not hotkey_combination:
                return False
            
            # Add the hotkey to our dictionary
            self._hotkeys[hotkey_combination] = callback
            
            # Start the listener with the updated hotkeys
            return self.start_listener()
            
        except Exception as e:
            print(f"Failed to register hotkey: {e}")
            return False
    
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
        try:
            # Parse hotkey string
            hotkey_combination = self.parse_hotkey_string(hotkey_str)
            
            # Check if hotkey is registered
            if not hotkey_combination or hotkey_combination not in self._hotkeys:
                return False
            
            # Stop listener
            self.stop_listener()
            
            # Remove hotkey from dictionary
            del self._hotkeys[hotkey_combination]
            
            # Restart listener if there are still hotkeys registered
            if self._hotkeys:
                return self.start_listener()
                
            return True
            
        except Exception as e:
            print(f"Failed to unregister hotkey: {e}")
            return False
    
    def set_recording_mode(self, enabled: bool, recording_hotkey: Optional[str] = None) -> None:
        """
        Set recording mode to filter hotkey events.
        
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
        prev_recording_mode = self._recording_mode
        
        self._recording_mode = enabled
        
        if enabled and recording_hotkey:
            # Parse and store the recording hotkey for filtering
            self._recording_hotkey = self.parse_hotkey_string(recording_hotkey)
            print(f"Recording mode enabled. Only hotkey '{recording_hotkey}' will be active.")
        else:
            # Reset recording hotkey when disabled
            self._recording_hotkey = None
            if not enabled:
                print("Recording mode disabled. All hotkeys are active.")
        
        # If listener is active and recording mode changed, restart the listener to apply the changes
        if self._listener_active and prev_recording_mode != self._recording_mode:
            self.stop_listener()
            self.start_listener()
    
    def start_listener(self) -> bool:
        """
        Start the hotkey listener.
        
        Returns
        -------
        bool
            True if the listener was started successfully.
        """
        try:
            # Only start if we have hotkeys to listen for
            if not self._hotkeys:
                return False
            
            # Create and start a listener with our hotkeys and event filtering
            if self._recording_mode:
                # In recording mode, we need to create a custom listener that filters events
                filtered_hotkeys = {}
                
                if self._recording_hotkey:
                    # Only include the recording hotkey if specified
                    for hotkey, callback in self._hotkeys.items():
                        if hotkey == self._recording_hotkey:
                            filtered_hotkeys[hotkey] = callback
                    
                    # Use filtered hotkeys if we're in recording mode
                    if filtered_hotkeys:
                        self._listener = keyboard.GlobalHotKeys(filtered_hotkeys)
                        print(f"Started hotkey listener in recording mode with 1 active hotkey")
                    else:
                        # If recording hotkey not found, use no hotkeys to effectively disable all
                        self._listener = keyboard.GlobalHotKeys({})
                        print(f"Warning: Recording hotkey not found in registered hotkeys. All hotkeys will be disabled.")
                else:
                    # If recording_hotkey is None in recording mode, disable all hotkeys
                    self._listener = keyboard.GlobalHotKeys({})
                    print("Disabled all hotkeys in recording mode with no active hotkey")
            else:
                # Normal mode, use all hotkeys
                self._listener = keyboard.GlobalHotKeys(self._hotkeys)
                print(f"Started hotkey listener with {len(self._hotkeys)} hotkeys")
            
            self._listener.start()
            self._listener_active = True
            
            return True
            
        except Exception as e:
            print(f"Failed to start hotkey listener: {e}")
            self._listener_active = False
            return False
    
    def stop_listener(self) -> bool:
        """
        Stop the hotkey listener.
        
        This method stops the listener without unregistering the hotkeys.
        
        Returns
        -------
        bool
            True if the listener was stopped successfully.
        """
        if self._listener and self._listener_active:
            try:
                self._listener.stop()
                self._listener = None
                self._listener_active = False
                print("Stopped hotkey listener")
                return True
            except Exception as e:
                print(f"Failed to stop hotkey listener: {e}")
        
        return False
    
    def restart_listener(self) -> bool:
        """
        Restart the hotkey listener.
        
        This method restarts the listener if it was previously stopped.
        
        Returns
        -------
        bool
            True if the listener was restarted successfully.
        """
        if self._listener_active or not self._hotkeys:
            return False
        
        return self.start_listener()
    
    def clear_all_hotkeys(self) -> bool:
        """
        Clear all registered hotkeys.
        
        Returns
        -------
        bool
            True if all hotkeys were cleared successfully.
        """
        # Stop the listener
        self.stop_listener()
        
        # Clear the hotkeys dictionary
        self._hotkeys.clear()
        
        return True
    
    @staticmethod
    def parse_hotkey_string(hotkey_str: str) -> Optional[str]:
        """
        Convert a user-friendly hotkey string to the format pynput expects.
        
        Parameters
        ----------
        hotkey_str : str
            User-friendly hotkey string (e.g., "ctrl+shift+r").
            
        Returns
        -------
        Optional[str]
            Pynput format hotkey string (e.g., "<ctrl>+<shift>+r"), or None if invalid.
        """
        if not hotkey_str:
            return None
        
        # Normalize to lowercase
        hotkey_str = hotkey_str.lower()
        
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
        parts = hotkey_str.split('+')
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
                print(f"Warning: Unknown key '{part}' in hotkey. Using as is.")
                processed_parts.append(part)
        
        # Return None if no valid parts were found
        if not processed_parts:
            return None
            
        # Join all parts with '+' to create the final hotkey string
        return '+'.join(processed_parts)
    
    def has_hotkey_conflict(self, hotkey_str: str) -> bool:
        """
        Check if a hotkey string conflicts with any registered hotkeys.
        
        Parameters
        ----------
        hotkey_str : str
            Hotkey string to check.
            
        Returns
        -------
        bool
            True if there is a conflict, False otherwise.
        """
        # Parse hotkey string
        hotkey_combination = self.parse_hotkey_string(hotkey_str)
        
        # Check if valid and already registered
        if not hotkey_combination:
            return False
            
        return hotkey_combination in self._hotkeys
    
    @staticmethod
    def is_valid_hotkey(hotkey_str: str) -> bool:
        """
        Check if a hotkey string is valid.
        
        Parameters
        ----------
        hotkey_str : str
            Hotkey string to check.
            
        Returns
        -------
        bool
            True if the hotkey string is valid, False otherwise.
        """
        return HotkeyManager.parse_hotkey_string(hotkey_str) is not None
    
    @staticmethod
    def contains_modifier(hotkey_str: str) -> bool:
        """
        Check if a hotkey string contains a modifier key.
        
        Parameters
        ----------
        hotkey_str : str
            Hotkey string to check.
            
        Returns
        -------
        bool
            True if the hotkey string contains a modifier key, False otherwise.
        """
        if not hotkey_str:
            return False
        
        modifiers = ['ctrl', 'control', 'alt', 'option', 'shift', 'cmd', 'command', 'win', 'windows', 'meta']
        parts = hotkey_str.lower().split('+')
        
        return any(part.strip() in modifiers for part in parts)