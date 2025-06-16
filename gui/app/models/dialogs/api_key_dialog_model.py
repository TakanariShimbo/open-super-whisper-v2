"""
API Key Management Model

This module provides functionality for API key validation and management.
"""

from PyQt6.QtCore import QObject

from core.api.api_checker import APIChecker

from ...managers.settings_manager import SettingsManager


class APIKeyDialogModel(QObject):
    """
    Model for API key dialog.

    This class encapsulates the functionality related to API key validation,
    storage, and retrieval.
    """

    def __init__(self, api_key_dialog: QObject | None = None) -> None:
        """
        Initialize the API Key Model.

        Parameters
        ----------
        api_key_dialog : QObject | None, optional
            The parent object, by default None
        """
        super().__init__(parent=api_key_dialog)

        self._settings_manager = SettingsManager.instance()

        # Load current API key
        self._openai_api_key = self._settings_manager.get_openai_api_key()

        # Store original value to support cancel operation
        self._original_openai_api_key = self._openai_api_key

    #
    # Model Methods
    #
    def validate_openai_api_key(self, openai_api_key: str) -> bool:
        """
        Validate an OpenAI API key using the API checker.

        Parameters
        ----------
        openai_api_key : str
            The OpenAI API key to validate

        Returns
        -------
        bool
            True if the OpenAI API key is valid, False otherwise
        """
        is_valid = APIChecker.check_openai_api_key(openai_api_key=openai_api_key)
        return is_valid

    def get_openai_api_key(self) -> str:
        """
        Get the current OpenAI API key value.

        Returns
        -------
        str
            The current OpenAI API key, or an empty string if none is set
        """
        return self._openai_api_key

    def set_openai_api_key(self, openai_api_key: str) -> None:
        """
        Set the OpenAI API key value.

        Parameters
        ----------
        openai_api_key : str
            The OpenAI API key to set
        """
        if self._openai_api_key != openai_api_key:
            self._openai_api_key = openai_api_key

    def save_openai_api_key(self) -> None:
        """
        Save current OpenAI API key to persistent storage.
        """
        self._settings_manager.set_openai_api_key(openai_api_key=self._openai_api_key)

        # Update original value
        self._original_openai_api_key = self._openai_api_key

    def restore_original(self) -> None:
        """
        Restore original OpenAI API key (cancel changes).
        """
        if self._openai_api_key != self._original_openai_api_key:
            self._openai_api_key = self._original_openai_api_key
