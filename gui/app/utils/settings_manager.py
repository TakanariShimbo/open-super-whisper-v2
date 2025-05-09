"""
Settings Manager

This module provides a centralized manager for application settings using QSettings.
It serves as a single point of interaction with QSettings to enforce consistent
access patterns and reduce direct dependencies on QSettings throughout the application.
"""

from typing import Any
from PyQt6.QtCore import QSettings


class SettingsManager:
    """
    Centralized manager for QSettings operations.
    
    This class provides a unified interface for interacting with QSettings,
    abstracting away direct QSettings dependencies from other parts of the application.
    It offers both generic methods for settings access and specific methods for
    commonly used settings.
    """
    
    # Define common setting keys as constants to avoid string duplication
    # and ensure consistency
    KEY_API_KEY = "api_key"
    KEY_INSTRUCTION_SETS = "instruction_sets"
    KEY_SELECTED_INSTRUCTION_SET = "selected_instruction_set"
    KEY_AUDIO_NOTIFICATIONS_ENABLED = "audio_notifications_enabled"
    KEY_AUDIO_NOTIFICATIONS_VOLUME = "audio_notifications_volume"
    KEY_INDICATOR_VISIBLE = "indicator_visible"
    KEY_AUTO_CLIPBOARD = "auto_clipboard"
    
    _instance = None

    @classmethod    
    def instance(cls) -> 'SettingsManager':
        """
        Get the singleton instance of the SettingsManager.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self) -> None:
        """
        Initialize the SettingsManager with a QSettings instance.

        Raises
        ------
        Exception
            If the SettingsManager is instantiated directly
        """
        if self._instance is not None:
            raise Exception("SettingsManager is a singleton class and cannot be instantiated directly.")
        
        self._instance = self
        self._settings = QSettings()
    
    def get_api_key(self) -> str:
        """
        Get the stored API key.
        
        Returns
        -------
        str
            The stored API key, or an empty string if none is stored
        """
        return self._settings.value(self.KEY_API_KEY, "", type=str)
    
    def set_api_key(self, api_key: str) -> None:
        """
        Store an API key.
        
        Parameters
        ----------
        api_key : str
            The API key to store
        """
        self._settings.setValue(self.KEY_API_KEY, api_key)
        self._settings.sync()
    
    def clear_api_key(self) -> None:
        """
        Clear the stored API key.
        """
        self._settings.remove(self.KEY_API_KEY)
        self._settings.sync()
    
    # Audio notification methods
    
    def get_audio_notifications_enabled(self) -> bool:
        """
        Check if audio notifications are enabled.
        
        Returns
        -------
        bool
            True if notifications are enabled, False otherwise
        """
        return self._settings.value(self.KEY_AUDIO_NOTIFICATIONS_ENABLED, True, type=bool)
    
    def set_audio_notifications_enabled(self, enabled: bool) -> None:
        """
        Set whether audio notifications are enabled.
        
        Parameters
        ----------
        enabled : bool
            True to enable notifications, False to disable
        """
        self._settings.setValue(self.KEY_AUDIO_NOTIFICATIONS_ENABLED, enabled)
        self._settings.sync()
    
    def get_audio_notifications_volume(self) -> float:
        """
        Get the volume level for audio notifications.
        
        Returns
        -------
        float
            Volume level between 0.0 and 1.0
        """
        return self._settings.value(self.KEY_AUDIO_NOTIFICATIONS_VOLUME, 0.7, type=float)
    
    def set_audio_notifications_volume(self, volume: float) -> None:
        """
        Set the volume level for audio notifications.
        
        Parameters
        ----------
        volume : float
            Volume level between 0.0 and 1.0
            
        Raises
        ------
        ValueError
            If the volume is outside the valid range
        """
        if not 0.0 <= volume <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")
        
        self._settings.setValue(self.KEY_AUDIO_NOTIFICATIONS_VOLUME, volume)
        self._settings.sync()
    
    # Instruction set methods
    
    def get_instruction_sets(self) -> Any:
        """
        Get the stored instruction sets.
        
        Returns
        -------
        Any
            The serialized instruction sets data, or None if not found
        """
        return self._settings.value(self.KEY_INSTRUCTION_SETS)
    
    def set_instruction_sets(self, instruction_sets_data: Any) -> None:
        """
        Store instruction sets data.
        
        Parameters
        ----------
        instruction_sets_data : Any
            The serialized instruction sets data to store
        """
        self._settings.setValue(self.KEY_INSTRUCTION_SETS, instruction_sets_data)
        self._settings.sync()
    
    def get_selected_instruction_set(self) -> str:
        """
        Get the name of the selected instruction set.
        
        Returns
        -------
        str
            The name of the selected instruction set, or an empty string if none selected
        """
        return self._settings.value(self.KEY_SELECTED_INSTRUCTION_SET, "", type=str)
    
    def set_selected_instruction_set(self, name: str) -> None:
        """
        Set the selected instruction set by name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to select
        """
        self._settings.setValue(self.KEY_SELECTED_INSTRUCTION_SET, name)
        self._settings.sync()
        
    # Status indicator visibility methods
    
    def get_indicator_visible(self) -> bool:
        """
        Check if status indicator should be visible.
        
        Returns
        -------
        bool
            True if indicator should be visible, False otherwise
        """
        return self._settings.value(self.KEY_INDICATOR_VISIBLE, True, type=bool)
    
    def set_indicator_visible(self, visible: bool) -> None:
        """
        Set whether status indicator should be visible.
        
        Parameters
        ----------
        visible : bool
            True to make indicator visible, False to hide
        """
        self._settings.setValue(self.KEY_INDICATOR_VISIBLE, visible)
        self._settings.sync()
    
    # Auto clipboard methods
    
    def get_auto_clipboard(self) -> bool:
        """
        Check if results should be automatically copied to clipboard.
        
        Returns
        -------
        bool
            True if auto-clipboard is enabled, False otherwise
        """
        return self._settings.value(self.KEY_AUTO_CLIPBOARD, False, type=bool)
    
    def set_auto_clipboard(self, enabled: bool) -> None:
        """
        Set whether results should be automatically copied to clipboard.
        
        Parameters
        ----------
        enabled : bool
            True to enable auto-clipboard, False to disable
        """
        self._settings.setValue(self.KEY_AUTO_CLIPBOARD, enabled)
        self._settings.sync()
