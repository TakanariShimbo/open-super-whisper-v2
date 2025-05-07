"""
Hotkey Manager Model

This module implements a model for managing hotkeys in the MVC architecture.
It leverages the core HotkeyManager class to handle the actual hotkey registration
and interaction with the operating system.
"""

from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal

from core.hotkey.hotkey_manager import HotkeyManager


class HotkeyModel(QObject):
    """
    Model for managing application hotkeys.
    
    This class serves as a wrapper around the core HotkeyManager class,
    providing a safe interface for registering and handling hotkeys within
    the Qt MVC architecture.
    
    Attributes
    ----------
    hotkey_triggered : pyqtSignal
        Signal emitted when a registered hotkey is triggered
    _hotkey_manager : HotkeyManager
        The core hotkey manager instance
    _task_hotkey : Optional[str]
        The current task hotkey
    """
    
    # Signal to notify when a hotkey is triggered
    hotkey_triggered = pyqtSignal(str)
    
    def __init__(self) -> None:
        """
        Initialize the HotkeyModel.
        
        Creates a new instance of the core HotkeyManager and sets up
        necessary internal state.
        """
        super().__init__()
        
        # Create the core hotkey manager
        self._hotkey_manager = HotkeyManager()
        
        # Store current task hotkey
        self._task_hotkey: Optional[str] = None
    
    @property
    def task_hotkey(self) -> Optional[str]:
        """
        Get the current task hotkey.
        
        Returns
        -------
        Optional[str]
            The current task hotkey or None if not set
        """
        return self._task_hotkey
    
    @task_hotkey.setter
    def task_hotkey(self, hotkey: Optional[str]) -> None:
        """
        Set the task hotkey.
        
        Parameters
        ----------
        hotkey : Optional[str]
            The hotkey to set for task control
        """
        # If we already have a task hotkey registered, unregister it
        if self._task_hotkey:
            self.unregister_hotkey(self._task_hotkey)
        
        # Store the new task hotkey
        self._task_hotkey = hotkey
        
        # Register the new task hotkey if provided
        if hotkey:
            self.register_hotkey(hotkey, lambda: self.hotkey_triggered.emit(hotkey))
    
    def register_hotkey(self, hotkey_str: str, callback: Callable) -> bool:
        """
        Register a hotkey.
        
        Parameters
        ----------
        hotkey_str : str
            The hotkey string (e.g., "ctrl+shift+r")
        callback : Callable
            The function to call when the hotkey is triggered
            
        Returns
        -------
        bool
            True if registration was successful, False otherwise
        """
        try:
            # Stop listening before making changes
            if self._hotkey_manager.is_listening:
                self._hotkey_manager.stop_listening()
            
            # Register the hotkey
            self._hotkey_manager.register_hotkey(
                hotkey_str,
                callback
            )
            
            # Restart listening if possible
            if self._hotkey_manager._hotkeys:  # Directly access HotkeyManager's hotkeys
                self._hotkey_manager.start_listening()
                
            return True
        except Exception as e:
            print(f"Error registering hotkey '{hotkey_str}': {e}")
            return False
    
    def unregister_hotkey(self, hotkey_str: str) -> bool:
        """
        Unregister a hotkey.
        
        Parameters
        ----------
        hotkey_str : str
            The hotkey string to unregister
            
        Returns
        -------
        bool
            True if unregistration was successful, False otherwise
        """
        try:
            # Stop listening before making changes
            if self._hotkey_manager.is_listening:
                self._hotkey_manager.stop_listening()
            
            # Unregister from hotkey manager
            result = self._hotkey_manager.unregister_hotkey(hotkey_str)
            
            # Restart listening if there are remaining hotkeys
            if self._hotkey_manager._hotkeys:  # Directly access HotkeyManager's hotkeys
                self._hotkey_manager.start_listening()
                
            return result
        except Exception as e:
            print(f"Error unregistering hotkey '{hotkey_str}': {e}")
            return False
    
    def is_valid_hotkey(self, hotkey_str: str) -> bool:
        """
        Check if a hotkey string is valid.
        
        Parameters
        ----------
        hotkey_str : str
            The hotkey string to check
            
        Returns
        -------
        bool
            True if the hotkey string is valid, False otherwise
        """
        return self._hotkey_manager.parse_hotkey_string(hotkey_str) is not None
    
    def clear_all_hotkeys(self) -> None:
        """
        Clear all registered hotkeys.
        """
        try:
            # Stop listening before making changes
            if self._hotkey_manager.is_listening:
                self._hotkey_manager.stop_listening()
            
            # Clear all hotkeys
            self._hotkey_manager.clear_all_hotkeys()
            
            # Reset task hotkey
            self._task_hotkey = None
        except Exception as e:
            print(f"Error clearing hotkeys: {e}")
