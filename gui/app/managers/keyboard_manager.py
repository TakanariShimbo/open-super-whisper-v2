"""
Keyboard Manager

This module provides the manager component for managing keyboard events
in the Super Whisper application.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from core.key.key_formatter import KeyFormatter
from core.key.key_state_tracker import KeyStateTracker
from core.key.hotkey_manager import HotkeyManager


class KeyboardManager(QObject):
    """
    Manager for managing keyboard events.
    
    This class provides a manager for managing keyboard events

    Attributes
    ----------
    hotkey_triggered : pyqtSignal
        Signal emitted when a registered hotkey is triggered
    """
    
    # Define signals
    hotkey_triggered = pyqtSignal(str)

    # Singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls) -> "KeyboardManager":
        """
        Get the singleton instance of the KeyboardManager.

        Returns
        -------
        KeyboardManager
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize the KeyboardManager.

        Raises
        ------
        Exception
            If the KeyboardManager is instantiated directly
        """
        super().__init__()
        
        # Check if singleton already exists
        if self._instance is not None:
            # If this is not the first instantiation, don't reinitialize
            raise Exception("KeyboardManager is a singleton class and cannot be instantiated directly.")

        self._instance = self
        
        # Initialize the underlying hotkey manager
        self._hotkey_manager = HotkeyManager()
        self._key_state_tracker = KeyStateTracker()
        
    @property
    def is_listening(self) -> bool:
        """
        Check if the keyboard manager is listening for hotkeys.
        
        Returns
        -------
        bool
            True if listening for hotkeys, False otherwise
        """
        return self._hotkey_manager.is_listening
    
    @property
    def is_filter_mode(self) -> bool:
        """
        Check if filter mode is active.
        
        Returns
        -------
        bool
            True if filter mode is active, False otherwise
        """
        return self._hotkey_manager.is_filter_mode_active
    
    @property
    def is_monitoring(self) -> bool:
        """
        Check if key monitoring mode is active.
        
        Returns
        -------
        bool
            True if monitoring key inputs, False otherwise
        """
        return self._key_state_tracker.is_monitoring
    
    # Key State Tracker methods

    def start_monitoring(self) -> None:
        """
        Start monitoring keyboard inputs.
        
        This method activates the key state tracker to monitor key combinations.
        """
        # Stop listening
        self.stop_listening()
        
        # Start monitoring
        if not self.is_monitoring:
            self._key_state_tracker.start_monitoring()
    
    def stop_monitoring(self) -> None:
        """
        Stop monitoring keyboard inputs.
        
        This method stops the key state tracker from monitoring key combinations.
        """
        # Stop monitoring
        if self.is_monitoring:
            self._key_state_tracker.stop_monitoring()
    
    def capture_last_keys(self) -> list[str]:
        """
        Capture and process the last key combination.
        
        This method reads the last keys from the key state tracker,
        formats them into a hotkey string, and updates the model.

        Returns
        -------
        list[str]
            The current key combination
        """
        # Check if monitoring is active
        if not self.is_monitoring:
            return
            
        # Get the last key combination from the tracker
        keys_list = self._key_state_tracker.get_last_keys()
                
        return keys_list
    
    # Hotkey Manager methods

    def get_active_hotkey(self) -> str | None:
        """
        Get the active hotkey.
        
        Returns
        -------
        str | None
            The active hotkey, or None if not in filter mode
        """
        active_hotkeys = self._hotkey_manager.get_active_hotkeys()
        if active_hotkeys:
            return active_hotkeys[0]
        return None
    
    def enable_filtered_mode_and_start_listening(self, active_hotkey: str) -> None:
        """
        Enable filtered mode with the active hotkey and start listening.

        In filter mode, only the active hotkey is enabled and
        all other hotkeys are filtered out.

        Parameters
        ----------
        active_hotkey : str, optional
            The hotkey that triggered filter mode, by default ""
        """
        # Stop listening
        self.stop_listening()
            
        # Enable filter mode with the active hotkey
        if active_hotkey:
            self._hotkey_manager.enable_filtered_mode([active_hotkey])
        else:
            # If no active hotkey provided, disable all hotkeys
            self._hotkey_manager.enable_filtered_mode([])
            
        # Start listening again
        self.start_listening()

    def disable_filtered_mode_and_start_listening(self) -> None:
        """
        Disable filtered mode and start listening.

        When disabled, all hotkeys are enabled again.
        """
        # Stop listening
        self.stop_listening()
            
        # Disable filtered mode
        self._hotkey_manager.disable_filtered_mode()
        
        # Start listening again
        self.start_listening()
    
    def register_hotkey(self, hotkey: str) -> bool:
        """
        Register a hotkey.
        
        Parameters
        ----------
        hotkey : str
            Hotkey string to register
        callback : Callable
            Callback function to call when the hotkey is triggered

        Returns
        -------
        bool
            True if registration was successful, False otherwise
        """
        # Define the callback function
        callback = lambda: self.hotkey_triggered.emit(hotkey)

        # Check if we need to stop the listener first
        was_listening = False
        if self.is_listening:
            was_listening = True
            self.stop_listening()
        
        # Register the hotkey with a callback that emits the signal
        try:
            self._hotkey_manager.register_hotkey(
                hotkey, 
                callback
            )
        except ValueError:
            return False
        
        # Restart listener if it was active
        if was_listening:
            self.start_listening()
            
        return True
    
    def unregister_hotkey(self, hotkey: str) -> bool:
        """
        Unregister a hotkey.
        
        Parameters
        ----------
        hotkey : str
            Hotkey string to unregister
            
        Returns
        -------
        bool
            True if unregistration was successful, False otherwise
        """
        # Check if we need to stop the listener first
        was_listening = False
        if self.is_listening:
            was_listening = True
            self.stop_listening()
        
        # Remove the hotkey from the manager
        result = self._hotkey_manager.unregister_hotkey(hotkey)
        
        # Restart listener if it was active and we still have hotkeys
        if was_listening:
            self.start_listening()
            
        return result
    
    def start_listening(self) -> bool:
        """
        Start listening for hotkeys.
        
        Returns
        -------
        bool
            True if listening started successfully, False otherwise
        """
        # Stop monitoring
        self.stop_monitoring()
        
        # Check if we have any registered hotkeys
        if not self._hotkey_manager.get_registered_hotkeys():
            return False
            
        # Start listening
        if not self._hotkey_manager.is_listening:
            self._hotkey_manager.start_listening()
        return True
    
    def stop_listening(self) -> bool:
        """
        Stop listening for hotkeys.
        
        Returns
        -------
        bool
            True if listening was stopped, False if it wasn't active
        """
        return self._hotkey_manager.stop_listening()
    
    def get_all_registered_hotkeys(self) -> list[str]:
        """
        Get a list of all registered hotkeys.
        
        Returns
        -------
        list[str]
            List of registered hotkey strings
        """
        return self._hotkey_manager.get_registered_hotkeys()

    # Key Formatter methods

    def parse_hotkey_string(self, hotkey_string: str) -> str:
        """
        Parse a hotkey string.
        """
        return KeyFormatter.parse_hotkey_string(hotkey_string)
