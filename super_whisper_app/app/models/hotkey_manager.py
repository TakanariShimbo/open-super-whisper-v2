"""
Hotkey Manager Module

This module provides the HotkeyModel class for managing global hotkeys
for controlling the application.
"""

from typing import Dict, Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal

# Import the core hotkey manager to use for actual hotkey registration
from core.hotkey.hotkey_manager import HotkeyManager as CoreHotkeyManager


class HotkeyModel(QObject):
    """
    Model for managing global hotkeys.
    
    This class provides functionality for registering, validating,
    and managing hotkeys for application control.
    
    Attributes
    ----------
    hotkey_triggered : pyqtSignal
        Signal emitted when a registered hotkey is triggered
    """
    
    # Signal emitted when a hotkey is triggered
    hotkey_triggered = pyqtSignal(str)
    
    def __init__(self) -> None:
        """
        Initialize the HotkeyModel.
        
        Sets up the core hotkey manager and initializes state.
        """
        super().__init__()
        
        # Core hotkey manager for actual hotkey registration
        self._core_manager = CoreHotkeyManager()
        
        # Hotkey state
        self._task_hotkey = ""  # Current task hotkey
        self._registered_hotkeys: Dict[str, str] = {}  # Map hotkey string to internal id
        
        # We don't start listening yet as we don't have any hotkeys registered
        # The listening will start when the first hotkey is registered
    
    def _emit_hotkey_triggered(self, hotkey: str) -> None:
        """
        Emit the hotkey_triggered signal.
        
        This is a callback for when hotkeys are pressed.
        
        Parameters
        ----------
        hotkey : str
            The hotkey that was pressed
        """
        self.hotkey_triggered.emit(hotkey)
    
    @property
    def task_hotkey(self) -> str:
        """
        Get the current task hotkey.
        
        Returns
        -------
        str
            The current task hotkey or empty string if not set
        """
        return self._task_hotkey
    
    @task_hotkey.setter
    def task_hotkey(self, hotkey: str) -> None:
        """
        Set the task hotkey.
        
        Parameters
        ----------
        hotkey : str
            The hotkey string to set
        
        Raises
        ------
        ValueError
            If the hotkey is not valid
        """
        if not self.is_valid_hotkey(hotkey):
            raise ValueError(f"Invalid hotkey: {hotkey}")
        
        # Stop listening to unregister existing hotkeys
        if self._core_manager.is_listening:
            self._core_manager.stop_listening()
        
        # Unregister old hotkey if set
        if self._task_hotkey:
            self._core_manager.unregister_hotkey(self._task_hotkey)
            if self._task_hotkey in self._registered_hotkeys:
                del self._registered_hotkeys[self._task_hotkey]
        
        # Register new hotkey
        if hotkey:
            # We need to create a lambda that captures the current value of hotkey
            callback = lambda hotkey=hotkey: self._emit_hotkey_triggered(hotkey)
            self._core_manager.register_hotkey(hotkey, callback)
            self._registered_hotkeys[hotkey] = hotkey
        
        # Store new hotkey
        self._task_hotkey = hotkey
        
        # Start listening again if we have registered hotkeys
        if hotkey or self._registered_hotkeys:
            try:
                self._core_manager.start_listening()
            except RuntimeError:
                # Ignore runtime error if no hotkeys are registered
                pass
    
    def is_valid_hotkey(self, hotkey: str) -> bool:
        """
        Check if a hotkey string is valid.
        
        Parameters
        ----------
        hotkey : str
            The hotkey string to check
            
        Returns
        -------
        bool
            True if the hotkey is valid, False otherwise
        """
        # Empty string is valid (disables hotkey)
        if not hotkey:
            return True
        
        # Delegate validation to core manager
        return self._core_manager.parse_hotkey_string(hotkey) is not None
    
    def register_hotkey(self, hotkey: str, callback: Optional[Callable] = None) -> bool:
        """
        Register a hotkey with an optional custom callback.
        
        If no callback is provided, the hotkey_triggered signal is emitted
        with the hotkey string.
        
        Parameters
        ----------
        hotkey : str
            The hotkey string to register
        callback : Optional[Callable], optional
            Custom callback function to call when the hotkey is pressed, by default None
            
        Returns
        -------
        bool
            True if the hotkey was registered, False otherwise
        """
        # Validate hotkey
        if not self.is_valid_hotkey(hotkey):
            return False
        
        # Stop listening to unregister existing hotkeys
        if self._core_manager.is_listening:
            self._core_manager.stop_listening()
        
        # Register with core manager
        try:
            # Use provided callback or default to emitting signal
            if callback is None:
                callback = lambda hotkey=hotkey: self._emit_hotkey_triggered(hotkey)
            
            self._core_manager.register_hotkey(hotkey, callback)
            self._registered_hotkeys[hotkey] = hotkey
            
            # Start listening again if we have hotkeys registered
            if self._registered_hotkeys:
                try:
                    self._core_manager.start_listening()
                except RuntimeError:
                    # Ignore runtime error if no hotkeys are registered
                    pass
            return True
        except Exception:
            # Start listening again if we have hotkeys registered
            if self._registered_hotkeys:
                try:
                    self._core_manager.start_listening()
                except RuntimeError:
                    # Ignore runtime error if no hotkeys are registered
                    pass
            return False
    
    def unregister_hotkey(self, hotkey: str) -> bool:
        """
        Unregister a hotkey.
        
        Parameters
        ----------
        hotkey : str
            The hotkey string to unregister
            
        Returns
        -------
        bool
            True if the hotkey was unregistered, False otherwise
        """
        if hotkey not in self._registered_hotkeys:
            return False
        
        try:
            # Stop listening to unregister existing hotkeys
            if self._core_manager.is_listening:
                self._core_manager.stop_listening()
            
            # Unregister from core manager
            self._core_manager.unregister_hotkey(hotkey)
            del self._registered_hotkeys[hotkey]
            
            # Start listening again if we have hotkeys registered
            if self._registered_hotkeys:
                try:
                    self._core_manager.start_listening()
                except RuntimeError:
                    # Ignore runtime error if no hotkeys are registered
                    pass
            return True
        except Exception:
            # Start listening again if we have hotkeys registered
            if self._registered_hotkeys:
                try:
                    self._core_manager.start_listening()
                except RuntimeError:
                    # Ignore runtime error if no hotkeys are registered
                    pass
            return False
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        This method should be called when the application is closing.
        """
        # Stop listening for hotkeys if listening
        if self._core_manager.is_listening:
            self._core_manager.stop_listening()
