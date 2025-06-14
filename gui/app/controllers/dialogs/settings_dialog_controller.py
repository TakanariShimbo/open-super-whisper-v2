"""
Settings Dialog Controller

This module provides the controller component for the settings dialog,
mediating between the model and view.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from ...models.dialogs.settings_dialog_model import SettingsDialogModel
from ...managers.keyboard_manager import KeyboardManager


class SettingsDialogController(QObject):
    """
    Controller for the settings dialog.

    This class mediates between the settings dialog view and model,
    handling user interactions and updating the model and view accordingly.

    Attributes
    ----------
    settings_updated : pyqtSignal
        Signal emitted when any settings are updated
    """

    #
    # Signals
    #
    settings_updated = pyqtSignal()

    def __init__(self, settings_dialog: QObject | None = None) -> None:
        """
        Initialize the SettingsDialogController.

        Parameters
        ----------
        settings_dialog : QObject | None, optional
            The parent object, by default None
        """
        super().__init__(parent=settings_dialog)

        # Create model
        self._dialog_model = SettingsDialogModel(settings_dialog=settings_dialog)
        
        # Get keyboard manager for hotkey control
        self._keyboard_manager = KeyboardManager.get_instance()

        # Connect model signals
        self._connect_model_signals()

    #
    # Model Signals
    #
    def _connect_model_signals(self) -> None:
        """
        Connect signals from the model to controller handlers.
        """
        # Connect the model's settings_updated signal to our handler
        self._dialog_model.settings_updated.connect(self._handle_settings_updated)

    #
    # Model Events
    #
    @pyqtSlot()
    def _handle_settings_updated(self) -> None:
        """
        Handle any settings change from the model.
        """
        # Notify view that settings have changed
        self.settings_updated.emit()

    #
    # Controller Methods
    #
    def get_sound_enabled(self) -> bool:
        """
        Get current sound enabled setting.

        Returns
        -------
        bool
            True if sound is enabled, False otherwise
        """
        return self._dialog_model.get_sound_enabled()

    def set_sound_enabled(self, enabled: bool) -> None:
        """
        Set sound enabled setting.

        Parameters
        ----------
        enabled : bool
            True to enable sound, False to disable
        """
        self._dialog_model.set_sound_enabled(value=enabled)

    def get_indicator_visible(self) -> bool:
        """
        Get current indicator visibility setting.

        Returns
        -------
        bool
            True if indicator should be visible, False otherwise
        """
        return self._dialog_model.get_indicator_visible()

    def set_indicator_visible(self, visible: bool) -> None:
        """
        Set indicator visibility setting.

        Parameters
        ----------
        visible : bool
            True to make indicator visible, False to hide
        """
        self._dialog_model.set_indicator_visible(value=visible)

    def get_auto_clipboard(self) -> bool:
        """
        Get current auto clipboard setting.

        Returns
        -------
        bool
            True if auto-clipboard is enabled, False otherwise
        """
        return self._dialog_model.get_auto_clipboard()

    def set_auto_clipboard(self, enabled: bool) -> None:
        """
        Set auto clipboard setting.

        Parameters
        ----------
        enabled : bool
            True to enable auto-clipboard, False to disable
        """
        self._dialog_model.set_auto_clipboard(value=enabled)

    def get_language(self) -> str:
        """
        Get current application language setting.

        Returns
        -------
        str
            The selected language name
        """
        return self._dialog_model.get_language()

    def set_language(self, language: str) -> None:
        """
        Set application language setting.

        Parameters
        ----------
        language : str
            The language name to set
        """
        self._dialog_model.set_language(value=language)

    def get_available_languages(self) -> list[str]:
        """
        Get the list of available languages.

        Returns
        -------
        list[str]
            List of available language names
        """
        return self._dialog_model.get_available_languages()

    def save_settings(self) -> None:
        """
        Save current settings to persistent storage and update related components.
        """
        # Save settings to persistent storage
        self._dialog_model.save_settings()

    def cancel(self) -> None:
        """
        Cancel dialog and restore original settings.
        """
        self._dialog_model.restore_original()

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
            True if listening stopped successfully, False otherwise
        """
        return self._keyboard_manager.stop_listening()
