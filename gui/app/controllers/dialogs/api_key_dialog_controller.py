"""
API Key Controller

This module provides the controller component for API key management.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from ...models.dialogs.api_key_dialog_model import APIKeyDialogModel
from ...managers.keyboard_manager import KeyboardManager


class APIKeyDialogController(QObject):
    """
    Controller for API key dialog.

    This class coordinates between the API key dialog model and view components,
    handling user interactions and business logic.

    Signals
    -------
    api_key_validated : pyqtSignal
        Signal emitted when an API key is validated successfully
    api_key_invalid : pyqtSignal
        Signal emitted when an API key validation fails
    """

    #
    # Signals
    #
    api_key_validated = pyqtSignal()
    api_key_invalid = pyqtSignal()

    def __init__(self, api_key_dialog: QObject | None = None) -> None:
        """
        Initialize the API Key Controller.

        Parameters
        ----------
        api_key_dialog : QObject | None, optional
            The parent object, by default None
        """
        super().__init__(parent=api_key_dialog)

        # Initialize the model
        self._model = APIKeyDialogModel(api_key_dialog=api_key_dialog)
        
        # Get keyboard manager for hotkey control
        self._keyboard_manager = KeyboardManager.get_instance()

    #
    # Controller Methods
    #
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate the given API key.

        Parameters
        ----------
        api_key : str
            The API key to validate

        Returns
        -------
        bool
            True if the API key is valid, False otherwise
        """
        # Validate the API key
        is_valid = self._model.validate_api_key(api_key=api_key)

        if is_valid:
            # Set the valid key in the model
            self._model.set_api_key(api_key=api_key)

            # Emit signal for validation success
            self.api_key_validated.emit()
        else:
            # Emit signal for validation failure
            self.api_key_invalid.emit()

        return is_valid

    def get_api_key(self) -> str:
        """
        Get current API key.

        Returns
        -------
        str
            The current API key
        """
        return self._model.get_api_key()

    def set_api_key(self, api_key: str) -> None:
        """
        Set API key in model.

        Parameters
        ----------
        api_key : str
            The API key to set
        """
        self._model.set_api_key(api_key=api_key)

    def save_api_key(self) -> None:
        """
        Save current API key to persistent storage.
        """
        self._model.save_api_key()

    def cancel(self) -> None:
        """
        Cancel dialog and restore original API key.
        """
        self._model.restore_original()

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
