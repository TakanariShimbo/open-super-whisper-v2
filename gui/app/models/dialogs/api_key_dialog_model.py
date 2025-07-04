"""
API Key Management Model

This module provides functionality for API key validation and management.
"""

from PyQt6.QtCore import QObject

from core.api.api_key_checker import APIKeyChecker

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
        self._anthropic_api_key = self._settings_manager.get_anthropic_api_key()
        self._gemini_api_key = self._settings_manager.get_gemini_api_key()

        # Store original value to support cancel operation
        self._original_openai_api_key = self._openai_api_key
        self._original_anthropic_api_key = self._anthropic_api_key
        self._original_gemini_api_key = self._gemini_api_key

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
            True if the API key is valid, False otherwise
        """
        return APIKeyChecker.check_openai_api_key(openai_api_key=openai_api_key)
    
    def validate_anthropic_api_key(self, anthropic_api_key: str) -> bool:
        """
        Validate an Anthropic API key using the API checker.

        Parameters
        ----------
        anthropic_api_key : str
            The Anthropic API key to validate

        Returns
        -------
        bool
            True if the API key is valid, False otherwise
        """
        return APIKeyChecker.check_anthropic_api_key(anthropic_api_key=anthropic_api_key)
    
    def validate_gemini_api_key(self, gemini_api_key: str) -> bool:
        """
        Validate a Gemini API key using the API checker.

        Parameters
        ----------
        gemini_api_key : str
            The Gemini API key to validate

        Returns
        -------
        bool
            True if the API key is valid, False otherwise
        """
        return APIKeyChecker.check_gemini_api_key(gemini_api_key=gemini_api_key)

    def get_openai_api_key(self) -> str:
        """
        Get the current OpenAI API key value.

        Returns
        -------
        str
            The current OpenAI API key, or an empty string if none is set
        """
        return self._openai_api_key

    def get_anthropic_api_key(self) -> str:
        """
        Get the current Anthropic API key value.

        Returns
        -------
        str
            The current Anthropic API key, or an empty string if none is set
        """
        return self._anthropic_api_key

    def get_gemini_api_key(self) -> str:
        """
        Get the current Gemini API key value.

        Returns
        -------
        str
            The current Gemini API key, or an empty string if none is set
        """
        return self._gemini_api_key

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

    def set_anthropic_api_key(self, anthropic_api_key: str) -> None:
        """
        Set the Anthropic API key value.

        Parameters
        ----------
        anthropic_api_key : str
            The Anthropic API key to set
        """
        if self._anthropic_api_key != anthropic_api_key:
            self._anthropic_api_key = anthropic_api_key

    def set_gemini_api_key(self, gemini_api_key: str) -> None:
        """
        Set the Gemini API key value.

        Parameters
        ----------
        gemini_api_key : str
            The Gemini API key to set
        """
        if self._gemini_api_key != gemini_api_key:
            self._gemini_api_key = gemini_api_key

    def save_api_key(self) -> None:
        """
        Save current OpenAI API key to persistent storage.
        """
        self._settings_manager.set_openai_api_key(openai_api_key=self._openai_api_key)
        self._settings_manager.set_anthropic_api_key(anthropic_api_key=self._anthropic_api_key)
        self._settings_manager.set_gemini_api_key(gemini_api_key=self._gemini_api_key)

        # Update original values
        self._original_openai_api_key = self._openai_api_key
        self._original_anthropic_api_key = self._anthropic_api_key
        self._original_gemini_api_key = self._gemini_api_key

    def restore_original(self) -> None:
        """
        Restore original OpenAI API key (cancel changes).
        """
        if self._openai_api_key != self._original_openai_api_key:
            self._openai_api_key = self._original_openai_api_key
        if self._anthropic_api_key != self._original_anthropic_api_key:
            self._anthropic_api_key = self._original_anthropic_api_key
        if self._gemini_api_key != self._original_gemini_api_key:
            self._gemini_api_key = self._original_gemini_api_key
