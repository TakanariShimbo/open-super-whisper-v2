"""
Hotkey Model

This module provides the model component for managing global hotkeys
in the Super Whisper application.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from core.key.key_formatter import KeyFormatter
from core.key.hotkey_manager import HotkeyManager


class HotkeyModel(QObject):
    """
    Model for managing global hotkeys.
    
    This class encapsulates the core HotkeyManager functionality and provides
    a Qt-friendly interface with signals for hotkey events.
    
    Attributes
    ----------
    hotkey_triggered : pyqtSignal
        Signal emitted when a registered hotkey is triggered
    """
    
    # Define signals
    hotkey_triggered = pyqtSignal(str)
    
    def __init__(self):
        """
        Initialize the HotkeyModel.
        """
        super().__init__()
        
        # Initialize the underlying hotkey manager
        self._hotkey_manager = HotkeyManager()
    
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
    
    def enable_filtered_mode(self, active_hotkey: str = "") -> None:
        """
        Enable filtered mode with the active hotkey.

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

    def disable_filtered_mode(self) -> None:
        """
        Disable filtered mode.

        When disabled, all hotkeys are enabled again.
        """
        # Stop listening
        self.stop_listening()
            
        # Disable filtered mode
        self._hotkey_manager.disable_filtered_mode()
        
        # Start listening again
        self.start_listening()
    
    def is_valid_hotkey(self, hotkey: str) -> bool:
        """
        Check if a hotkey string is valid.
        
        Parameters
        ----------
        hotkey : str
            Hotkey string to validate
            
        Returns
        -------
        bool
            True if the hotkey is valid, False otherwise
        """
        return KeyFormatter.parse_hotkey_string(hotkey) is not None
    
    def register_hotkey(self, hotkey: str) -> bool:
        """
        Register a hotkey.
        
        Parameters
        ----------
        hotkey : str
            Hotkey string to register
            
        Returns
        -------
        bool
            True if registration was successful, False otherwise
        """
        # Check if hotkey is valid
        if not self.is_valid_hotkey(hotkey):
            return False
        
        # Check if we need to stop the listener first
        was_listening = False
        if self._hotkey_manager.is_listening:
            was_listening = True
            self._hotkey_manager.stop_listening()
        
        # Register the hotkey with a callback that emits the signal
        try:
            self._hotkey_manager.register_hotkey(
                hotkey, 
                lambda: self.hotkey_triggered.emit(hotkey)
            )
        except (ValueError, RuntimeError):
            return False
        
        # Restart listener if it was active
        if was_listening:
            self._hotkey_manager.start_listening()
            
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
        if self._hotkey_manager.is_listening:
            was_listening = True
            self._hotkey_manager.stop_listening()
        
        # Remove the hotkey from the manager
        try:
            result = self._hotkey_manager.unregister_hotkey(hotkey)
        except (ValueError, RuntimeError):
            return False
        
        # Restart listener if it was active and we still have hotkeys
        if was_listening and self._hotkey_manager.get_registered_hotkeys():
            self._hotkey_manager.start_listening()
            
        return result
    
    def start_listening(self) -> bool:
        """
        Start listening for hotkeys.
        
        Returns
        -------
        bool
            True if listening started successfully, False otherwise
        """
        if not self._hotkey_manager.get_registered_hotkeys():
            return False
            
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
