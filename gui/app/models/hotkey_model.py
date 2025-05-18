"""
Hotkey Model

This module provides the model component for managing global hotkeys
in the Super Whisper application.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from ..managers.keyboard_manager import KeyboardManager


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
        self._keyboard_manager = KeyboardManager.get_instance()
        
        # Connect model signals
        self._connect_manager_signals()
    
    def _connect_manager_signals(self) -> None:
        """
        Connect signals from the manager to model handlers.
        """
        # Connect the manager's hotkey_triggered signal to our handler
        self._keyboard_manager.hotkey_triggered.connect(self._handle_hotkey_triggered)
    
    @pyqtSlot(str)
    def _handle_hotkey_triggered(self, hotkey: str) -> None:
        """
        Handle any hotkey triggered from the manager.
        """
        # Notify view that hotkey has been triggered
        self.hotkey_triggered.emit(hotkey)

    @property
    def is_filter_mode(self) -> bool:
        """
        Check if filter mode is active.
        
        Returns
        -------
        bool
            True if filter mode is active, False otherwise
        """
        return self._keyboard_manager.is_filter_mode
    
    def get_active_hotkey(self) -> str | None:
        """
        Get the active hotkey.
        
        Returns
        -------
        str | None
            The active hotkey, or None if not in filter mode
        """
        return self._keyboard_manager.get_active_hotkey()
    
    def enable_filtered_mode_and_start_listening(self, active_hotkey: str = "") -> None:
        """
        Enable filtered mode with the active hotkey.

        In filter mode, only the active hotkey is enabled and
        all other hotkeys are filtered out.

        Parameters
        ----------
        active_hotkey : str, optional
            The hotkey that triggered filter mode, by default ""
        """
        self._keyboard_manager.enable_filtered_mode_and_start_listening(active_hotkey)

    def disable_filtered_mode_and_start_listening(self) -> None:
        """
        Disable filtered mode.

        When disabled, all hotkeys are enabled again.
        """
        self._keyboard_manager.disable_filtered_mode_and_start_listening()
    
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
        return self._keyboard_manager.register_hotkey(hotkey)
    
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
        return self._keyboard_manager.unregister_hotkey(hotkey)
    
    def start_listening(self) -> bool:
        """
        Start listening for hotkeys.
        
        Returns
        -------
        bool
            True if listening started successfully, False otherwise
        """
        return self._keyboard_manager.start_listening()
    
    def stop_listening(self) -> bool:
        """
        Stop listening for hotkeys.
        
        Returns
        -------
        bool
            True if listening was stopped, False if it wasn't active
        """
        return self._keyboard_manager.stop_listening()
    
    def get_all_registered_hotkeys(self) -> list[str]:
        """
        Get a list of all registered hotkeys.
        
        Returns
        -------
        list[str]
            List of registered hotkey strings
        """
        return self._keyboard_manager.get_all_registered_hotkeys()
