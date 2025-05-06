"""
Hotkey Model

This module provides a model class that interfaces with the core HotKeyManager.
It adapts the core functionality to fit into the MVC architecture.
"""
from typing import Callable, Dict
from PyQt6.QtCore import QObject, pyqtSignal

# Import the core hotkey manager
from core.ui.hot_key_manager import HotKeyManager

class HotKeyModel(QObject):
    """
    Model class that interfaces with the HotKeyManager.
    
    This class provides a bridge between the core HotKeyManager functionality 
    and the application's controller. It wraps the HotKeyManager methods and
    emits signals when hotkeys are triggered.
    
    Attributes
    ----------
    hotkey_registered : pyqtSignal
        Signal emitted when a hotkey is registered successfully
    hotkey_error : pyqtSignal
        Signal emitted when a hotkey error occurs
    """
    # Define signals for communication
    hotkey_registered = pyqtSignal(str)  # Emits the hotkey string
    hotkey_error = pyqtSignal(str)       # Emits error message
    
    def __init__(self) -> None:
        """
        Initialize the HotKeyModel.
        
        Creates an instance of the core HotKeyManager and sets up the model.
        """
        super().__init__()
        
        # Create the core hotkey manager
        self._hotkey_manager = HotKeyManager()
        
        # Dictionary to store the hotkey callbacks
        self._callbacks: Dict[str, Callable] = {}
        
    @property
    def is_listening(self) -> bool:
        """
        Check if the hotkey manager is currently listening for hotkeys.
        
        Returns
        -------
        bool
            True if the manager is actively listening, False otherwise
        """
        return self._hotkey_manager.is_listening
    
    def register_hotkey(self, hotkey_string: str, callback: Callable) -> bool:
        """
        Register a global hotkey.
        
        Parameters
        ----------
        hotkey_string : str
            String representation of the hotkey (e.g., "ctrl+shift+r")
        callback : Callable
            Function to call when the hotkey is pressed
            
        Returns
        -------
        bool
            True if registration was successful, False otherwise
            
        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first
        ValueError
            If the hotkey string is invalid
        """
        try:
            # Register the hotkey
            self._hotkey_manager.register_hotkey(hotkey_string, callback)
            
            # Store the callback for future reference
            self._callbacks[hotkey_string] = callback
            
            # Emit signal
            self.hotkey_registered.emit(hotkey_string)
            return True
        except Exception as e:
            error_message = f"Error registering hotkey: {str(e)}"
            self.hotkey_error.emit(error_message)
            return False
    
    def unregister_hotkey(self, hotkey_string: str) -> bool:
        """
        Unregister a previously registered global hotkey.
        
        Parameters
        ----------
        hotkey_string : str
            String representation of the hotkey to unregister
            
        Returns
        -------
        bool
            True if the hotkey was successfully unregistered, False if it was not registered
        
        Raises
        ------
        RuntimeError
            If the hotkey manager is currently listening and needs to be stopped first
        ValueError
            If the hotkey string is invalid
        """
        try:
            # Unregister the hotkey
            result = self._hotkey_manager.unregister_hotkey(hotkey_string)
            
            # Remove the callback if successfully unregistered
            if result and hotkey_string in self._callbacks:
                del self._callbacks[hotkey_string]
                
            return result
        except Exception as e:
            error_message = f"Error unregistering hotkey: {str(e)}"
            self.hotkey_error.emit(error_message)
            return False
    
    def start_listening(self) -> bool:
        """
        Start the hotkey listener.
        
        Returns
        -------
        bool
            True if the listener was started successfully, False otherwise
        """
        try:
            if not self.is_listening:
                self._hotkey_manager.start_listening()
                return True
            return False
        except Exception as e:
            error_message = f"Error starting hotkey listener: {str(e)}"
            self.hotkey_error.emit(error_message)
            return False
    
    def stop_listening(self) -> bool:
        """
        Stop the hotkey listener.
        
        Returns
        -------
        bool
            True if the listener was stopped, False if there was no active listener
        """
        try:
            return self._hotkey_manager.stop_listening()
        except Exception as e:
            error_message = f"Error stopping hotkey listener: {str(e)}"
            self.hotkey_error.emit(error_message)
            return False
