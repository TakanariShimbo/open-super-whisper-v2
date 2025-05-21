"""
Settings Dialog Model

This module provides the model component for the settings dialog,
handling the data and business logic related to application settings.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from ...managers.settings_manager import SettingsManager
from ...managers.audio_manager import AudioManager


class SettingsDialogModel(QObject):
    """
    Model for the settings dialog.

    This class handles the data and business logic for the settings dialog,
    including managing and validating user preferences for audio notifications,
    status indicator visibility, and automatic clipboard operations.

    Attributes
    ----------
    settings_changed : pyqtSignal
        Signal emitted when any setting changes
    """

    # Define a single signal for any settings change
    settings_updated = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the SettingsDialogModel.

        Parameters
        ----------
        parent : QObject, optional
            Parent object, by default None
        """
        super().__init__(parent=parent)

        # Get settings manager instance
        self._audio_manager = AudioManager.instance()
        self._settings_manager = SettingsManager.instance()

        # Load current settings
        self._sound_enabled = self._settings_manager.get_audio_notifications_enabled()
        self._indicator_visible = self._settings_manager.get_indicator_visible()
        self._auto_clipboard = self._settings_manager.get_auto_clipboard()

        # Store original values to support cancel operation
        self._original_sound_enabled = self._sound_enabled
        self._original_indicator_visible = self._indicator_visible
        self._original_auto_clipboard = self._auto_clipboard

    def get_sound_enabled(self) -> bool:
        """
        Get if sound notifications are enabled.

        Returns
        -------
        bool
            True if sound is enabled, False otherwise
        """
        return self._sound_enabled

    def set_sound_enabled(self, value: bool) -> None:
        """
        Set if sound notifications are enabled.

        Parameters
        ----------
        value : bool
            True to enable sound, False to disable
        """
        if self._sound_enabled != value:
            self._sound_enabled = value
            self.settings_updated.emit()

    def get_indicator_visible(self) -> bool:
        """
        Get if status indicator should be visible.

        Returns
        -------
        bool
            True if indicator should be visible, False otherwise
        """
        return self._indicator_visible

    def set_indicator_visible(self, value: bool) -> None:
        """
        Set if status indicator should be visible.

        Parameters
        ----------
        value : bool
            True to make indicator visible, False to hide
        """
        if self._indicator_visible != value:
            self._indicator_visible = value
            self.settings_updated.emit()

    def get_auto_clipboard(self) -> bool:
        """
        Get if results should be automatically copied to clipboard.

        Returns
        -------
        bool
            True if auto-clipboard is enabled, False otherwise
        """
        return self._auto_clipboard

    def set_auto_clipboard(self, value: bool) -> None:
        """
        Set if results should be automatically copied to clipboard.

        Parameters
        ----------
        value : bool
            True to enable auto-clipboard, False to disable
        """
        if self._auto_clipboard != value:
            self._auto_clipboard = value
            self.settings_updated.emit()

    def save_settings(self) -> None:
        """
        Save current settings to persistent storage.
        """
        self._audio_manager.set_enabled(value=self._sound_enabled)
        self._settings_manager.set_indicator_visible(visible=self._indicator_visible)
        self._settings_manager.set_auto_clipboard(enabled=self._auto_clipboard)

        # Update original values
        self._original_sound_enabled = self._sound_enabled
        self._original_indicator_visible = self._indicator_visible
        self._original_auto_clipboard = self._auto_clipboard

    def restore_original(self) -> None:
        """
        Restore original settings (cancel changes).
        """
        self.set_sound_enabled(value=self._original_sound_enabled)
        self.set_indicator_visible(value=self._original_indicator_visible)
        self.set_auto_clipboard(value=self._original_auto_clipboard)
