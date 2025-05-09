"""
Settings Dialog Model

This module provides the model component for the settings dialog, 
handling the data and business logic related to application settings.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from ...utils.settings_manager import SettingsManager


class SettingsDialogModel(QObject):
    """
    Model for the settings dialog.
    
    This class handles the data and business logic for the settings dialog,
    including managing and validating user preferences for audio notifications,
    status indicator visibility, and automatic clipboard operations.
    
    Attributes
    ----------
    sound_enabled_changed : pyqtSignal
        Signal emitted when sound enabled setting changes
    indicator_visible_changed : pyqtSignal
        Signal emitted when indicator visibility setting changes
    auto_clipboard_changed : pyqtSignal
        Signal emitted when auto clipboard setting changes
    """
    
    # Define signals for controller communication
    sound_enabled_changed = pyqtSignal(bool)
    indicator_visible_changed = pyqtSignal(bool)
    auto_clipboard_changed = pyqtSignal(bool)
    
    def __init__(self) -> None:
        """
        Initialize the SettingsDialogModel.
        
        Loads current settings from the SettingsManager.
        """
        super().__init__()
        
        # Get settings manager instance
        self._settings_manager = SettingsManager.instance()
        
        # Load current settings
        self._sound_enabled = self._settings_manager.get_audio_notifications_enabled()
        self._indicator_visible = self._settings_manager.get_indicator_visible()
        self._auto_clipboard = self._settings_manager.get_auto_clipboard()
        
        # Store original values to support cancel operation
        self._original_sound_enabled = self._sound_enabled
        self._original_indicator_visible = self._indicator_visible
        self._original_auto_clipboard = self._auto_clipboard
    
    @property
    def sound_enabled(self) -> bool:
        """
        Get if sound notifications are enabled.
        
        Returns
        -------
        bool
            True if sound is enabled, False otherwise
        """
        return self._sound_enabled
    
    @sound_enabled.setter
    def sound_enabled(self, value: bool) -> None:
        """
        Set if sound notifications are enabled.
        
        Parameters
        ----------
        value : bool
            True to enable sound, False to disable
        """
        if self._sound_enabled != value:
            self._sound_enabled = value
            self.sound_enabled_changed.emit(value)
    
    @property
    def indicator_visible(self) -> bool:
        """
        Get if status indicator should be visible.
        
        Returns
        -------
        bool
            True if indicator should be visible, False otherwise
        """
        return self._indicator_visible
    
    @indicator_visible.setter
    def indicator_visible(self, value: bool) -> None:
        """
        Set if status indicator should be visible.
        
        Parameters
        ----------
        value : bool
            True to make indicator visible, False to hide
        """
        if self._indicator_visible != value:
            self._indicator_visible = value
            self.indicator_visible_changed.emit(value)
    
    @property
    def auto_clipboard(self) -> bool:
        """
        Get if results should be automatically copied to clipboard.
        
        Returns
        -------
        bool
            True if auto-clipboard is enabled, False otherwise
        """
        return self._auto_clipboard
    
    @auto_clipboard.setter
    def auto_clipboard(self, value: bool) -> None:
        """
        Set if results should be automatically copied to clipboard.
        
        Parameters
        ----------
        value : bool
            True to enable auto-clipboard, False to disable
        """
        if self._auto_clipboard != value:
            self._auto_clipboard = value
            self.auto_clipboard_changed.emit(value)
    
    def save_settings(self) -> None:
        """
        Save current settings to persistent storage.
        """
        self._settings_manager.set_audio_notifications_enabled(self._sound_enabled)
        self._settings_manager.set_indicator_visible(self._indicator_visible)
        self._settings_manager.set_auto_clipboard(self._auto_clipboard)
        
        # Update original values
        self._original_sound_enabled = self._sound_enabled
        self._original_indicator_visible = self._indicator_visible
        self._original_auto_clipboard = self._auto_clipboard
    
    def restore_original(self) -> None:
        """
        Restore original settings (cancel changes).
        """
        self.sound_enabled = self._original_sound_enabled
        self.indicator_visible = self._original_indicator_visible
        self.auto_clipboard = self._original_auto_clipboard
