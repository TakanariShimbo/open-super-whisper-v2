"""
Hotkey Bridge Implementation

This module provides a bridge between the native hotkey system
and Qt's thread model, ensuring thread-safe hotkey handling.
"""

from PyQt6.QtCore import QObject, pyqtSignal, Qt
from typing import Callable, Optional

from core.ui.hot_key_manager import HotKeyManager

class HotkeyBridge(QObject):
    """
    Safe bridge between hotkey events and Qt UI thread
    
    This class converts events from HotkeyManager to Qt signals
    to ensure thread-safe operations.
    """
    
    # Singleton instance
    _instance = None
    
    # Signal definitions
    hotkeyTriggered = pyqtSignal(str)  # hotkey_str
    _execute_callback = pyqtSignal(str)  # Internal signal for executing callbacks
    recordingHotkeyPressed = pyqtSignal(str)  # hotkey_str - Signal when an instruction set hotkey is pressed
    
    @classmethod
    def instance(cls) -> 'HotkeyBridge':
        """
        Get the singleton instance
        
        Returns
        -------
        HotkeyBridge
            Singleton instance
        """
        if cls._instance is None:
            cls._instance = HotkeyBridge()
        return cls._instance
    
    def __init__(self):
        """
        Initialize HotkeyBridge
        """
        super().__init__()
        
        # Create local hotkey manager
        self.hotkey_manager = HotKeyManager()
        
        # Hotkey callback mapping
        self._hotkey_callbacks = {}
        
        # Recording state
        self._is_recording = False
        self._active_recording_hotkey = None
        
        # Connect internal signals
        self._execute_callback.connect(self._on_execute_callback, Qt.ConnectionType.QueuedConnection)
    
    def register_hotkey(self, hotkey_str: str, callback: Callable) -> bool:
        """
        Register a hotkey
        
        Parameters
        ----------
        hotkey_str : str
            Hotkey string (e.g., "ctrl+shift+r")
        callback : Callable
            Callback function to call when triggered
            
        Returns
        -------
        bool
            Whether registration was successful
        """
        # Save callback
        self._hotkey_callbacks[hotkey_str] = callback
        
        # Register with HotkeyManager
        # Use bridge function for registration
        return self.hotkey_manager.register_hotkey(
            hotkey_str,
            lambda: self._safe_trigger_callback(hotkey_str)
        )
    
    def unregister_hotkey(self, hotkey_str: str) -> bool:
        """
        Unregister a hotkey
        
        Parameters
        ----------
        hotkey_str : str
            Hotkey string
            
        Returns
        -------
        bool
            Whether unregistration was successful
        """
        # Unregister from HotkeyManager
        result = self.hotkey_manager.unregister_hotkey(hotkey_str)
        
        # Remove from callback dictionary
        if hotkey_str in self._hotkey_callbacks:
            del self._hotkey_callbacks[hotkey_str]
        
        return result
    
    # Signal is defined at class level
    
    def _safe_trigger_callback(self, hotkey_str: str) -> None:
        """
        Safe execution of hotkey callback
        
        Parameters
        ----------
        hotkey_str : str
            Triggered hotkey string
        """
        # If we're recording and this is the active recording hotkey, 
        # emit recordingHotkeyPressed signal instead of normal callback
        if self._is_recording and hotkey_str == self._active_recording_hotkey:
            self.recordingHotkeyPressed.emit(hotkey_str)
        elif hotkey_str in self._hotkey_callbacks:
            # For non-recording case or different hotkeys
            # Use signal to execute callback in main thread
            self._execute_callback.emit(hotkey_str)
    
    def _on_execute_callback(self, hotkey_str: str) -> None:
        """
        Slot for executing the callback in the main thread
        
        Parameters
        ----------
        hotkey_str : str
            Triggered hotkey string
        """
        if hotkey_str in self._hotkey_callbacks:
            callback = self._hotkey_callbacks[hotkey_str]
            callback()
    
    def set_recording_mode(self, enabled: bool, recording_hotkey: Optional[str] = None) -> None:
        """
        Set recording mode
        
        Parameters
        ----------
        enabled : bool
            Whether to enable recording mode
        recording_hotkey : Optional[str], optional
            Recording hotkey string
        """
        self._is_recording = enabled
        self._active_recording_hotkey = recording_hotkey
        self.hotkey_manager.enable_recording_mode(enabled, recording_hotkey)
    
    def is_recording(self) -> bool:
        """
        Check if recording mode is active
        
        Returns
        -------
        bool
            Whether recording mode is active
        """
        return self._is_recording
    
    def get_active_recording_hotkey(self) -> Optional[str]:
        """
        Get the currently active recording hotkey
        
        Returns
        -------
        Optional[str]
            The active recording hotkey or None if not recording
        """
        return self._active_recording_hotkey
    
    def clear_all_hotkeys(self) -> bool:
        """
        Clear all hotkey registrations
        
        Returns
        -------
        bool
            Whether clearing was successful
        """
        result = self.hotkey_manager.clear_all_hotkeys()
        self._hotkey_callbacks.clear()
        return result
