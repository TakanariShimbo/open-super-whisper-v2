"""
Hotkey Model

This module provides the model component for managing global hotkeys
in the Super Whisper application.
"""

from typing import Dict, Callable, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from core.hotkey.hotkey_manager import HotkeyManager

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
        
        # Dictionary to store registered hotkeys and their handlers
        self._handlers: Dict[str, Callable] = {}
        
        # Currently active recording hotkey (during recording)
        self._active_recording_hotkey: Optional[str] = None
    
    @property
    def is_recording_mode_active(self) -> bool:
        """
        Check if recording mode is active.
        
        Returns
        -------
        bool
            True if recording mode is active, False otherwise
        """
        return self._active_recording_hotkey is not None
    
    def get_active_recording_hotkey(self) -> Optional[str]:
        """
        Get the active recording hotkey.
        
        Returns
        -------
        Optional[str]
            The active recording hotkey, or None if not in recording mode
        """
        return self._active_recording_hotkey
    
    def set_recording_mode(self, active: bool, active_hotkey: str = "") -> None:
        """
        Set recording mode active or inactive.
        
        In recording mode, only the active recording hotkey is enabled and
        all other hotkeys are filtered out.
        
        Parameters
        ----------
        active : bool
            True to enable recording mode, False to disable
        active_hotkey : str, optional
            The hotkey that triggered recording, by default ""
        """
        if active:
            # Enable recording mode
            self._active_recording_hotkey = active_hotkey
            
            if self._hotkey_manager.is_listening:
                self._hotkey_manager.stop_listening()
                
            # Set filtered mode to only allow the active hotkey
            if active_hotkey:
                self._hotkey_manager.enable_filtered_mode([active_hotkey])
            else:
                # If no active hotkey provided, disable all hotkeys
                self._hotkey_manager.enable_filtered_mode([])
                
            # Start listening again
            if self._handlers:
                self._register_handlers_with_manager()
                self._hotkey_manager.start_listening()
        else:
            # Disable recording mode
            self._active_recording_hotkey = None
            
            if self._hotkey_manager.is_listening:
                self._hotkey_manager.stop_listening()
                
            # Disable filtered mode
            self._hotkey_manager.disable_filtered_mode()
            
            # Start listening again
            if self._handlers:
                self._register_handlers_with_manager()
                self._hotkey_manager.start_listening()
    
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
        return HotkeyManager.parse_hotkey_string(hotkey) is not None
    
    def register_hotkey(self, hotkey: str, handler_id: str) -> bool:
        """
        Register a hotkey with a handler ID.
        
        Parameters
        ----------
        hotkey : str
            Hotkey string to register
        handler_id : str
            Unique ID for this hotkey handler
            
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
        
        # Store the handler
        self._handlers[hotkey] = lambda: self.hotkey_triggered.emit(hotkey)
        
        # Re-register all handlers
        self._register_handlers_with_manager()
        
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
        # Check if hotkey is registered
        if hotkey not in self._handlers:
            return False
            
        # Check if we need to stop the listener first
        was_listening = False
        if self._hotkey_manager.is_listening:
            was_listening = True
            self._hotkey_manager.stop_listening()
        
        # Remove the handler
        del self._handlers[hotkey]
        
        # Re-register all handlers
        self._register_handlers_with_manager()
        
        # Restart listener if it was active
        if was_listening and self._handlers:
            self._hotkey_manager.start_listening()
            
        return True
    
    def _register_handlers_with_manager(self) -> None:
        """
        Register all handlers with the hotkey manager.
        
        This internal method clears all existing hotkeys in the manager
        and registers the current set of handlers.
        """
        # Clear existing hotkeys in the manager
        self._hotkey_manager.clear_all_hotkeys()
        
        # Register each handler
        for hotkey, handler in self._handlers.items():
            try:
                self._hotkey_manager.register_hotkey(hotkey, handler)
            except (ValueError, RuntimeError):
                # Skip invalid hotkeys or runtime errors
                continue
    
    def start_listening(self) -> bool:
        """
        Start listening for hotkeys.
        
        Returns
        -------
        bool
            True if listening started successfully, False otherwise
        """
        if not self._handlers:
            return False
            
        try:
            if not self._hotkey_manager.is_listening:
                self._hotkey_manager.start_listening()
            return True
        except RuntimeError:
            return False
    
    def stop_listening(self) -> bool:
        """
        Stop listening for hotkeys.
        
        Returns
        -------
        bool
            True if listening was stopped, False if it wasn't active
        """
        return self._hotkey_manager.stop_listening()
    
    def clear_all_hotkeys(self) -> None:
        """
        Clear all registered hotkeys.
        """
        # Stop listening if active
        if self._hotkey_manager.is_listening:
            self._hotkey_manager.stop_listening()
            
        # Clear handlers
        self._handlers.clear()
        
        # Clear manager hotkeys
        self._hotkey_manager.clear_all_hotkeys()
    
    def get_all_registered_hotkeys(self) -> List[str]:
        """
        Get a list of all registered hotkeys.
        
        Returns
        -------
        List[str]
            List of registered hotkey strings
        """
        return list(self._handlers.keys())
