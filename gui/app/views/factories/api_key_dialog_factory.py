"""
API Key Dialog Factory

This module provides a factory for creating API key dialog instances,
following the factory design pattern to centralize dialog creation logic.
"""

from PyQt6.QtWidgets import QWidget

from ..dialogs.api_key_dialog import APIKeyDialog
from ...managers.settings_manager import SettingsManager


class LabelManager:
    """
    Manages application labels for internationalization support.
    """

    ALL_LABELS = {
        "English": {
            "initial_api_key_message": "Welcome to Open Super Whisper! Please enter your OpenAI API key to get started.",
            "settings_api_key_message": "Update your API key if needed.",
        },
        "Japanese": {
            "initial_api_key_message": "Open Super Whisperへようこそ! OpenAI APIキーを入力して開始してください。",
            "settings_api_key_message": "必要に応じてAPIキーを更新してください。",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # set labels based on language
        self._labels = self.ALL_LABELS[language]

    @property
    def initial_api_key_message(self) -> str:
        return self._labels["initial_api_key_message"]

    @property
    def settings_api_key_message(self) -> str:
        return self._labels["settings_api_key_message"]


class APIKeyDialogFactory:
    """
    Factory class for creating API key dialog instances.

    This class provides methods to create properly configured API key
    dialog instances with their controllers, following the MVC pattern.
    """

    @staticmethod
    def _create_dialog(
        initial_message: str,
        main_window: QWidget | None = None,
    ) -> APIKeyDialog:
        """
        Create a generic API key dialog instance.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget for the dialog, by default None
        initial_message : str, optional
            Initial message to display in the dialog, by default None

        Returns
        -------
        APIKeyDialog
            The created API key dialog instance
        """
        dialog = APIKeyDialog(
            initial_message=initial_message,
            main_window=main_window,
        )

        return dialog

    @classmethod
    def create_initial_dialog(cls) -> APIKeyDialog:
        """
        Create an API key dialog for initial application setup.

        Returns
        -------
        APIKeyDialog
            The created API key dialog instance
        """
        # Initialize label manager for internationalization
        label_manager = LabelManager()
        initial_message = label_manager.initial_api_key_message
        return cls._create_dialog(initial_message=initial_message)

    @classmethod
    def create_settings_dialog(cls, main_window: QWidget | None = None) -> APIKeyDialog:
        """
        Create an API key dialog for settings/update.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget for the dialog, by default None

        Returns
        -------
        APIKeyDialog
            The created API key dialog instance
        """
        # Initialize label manager for internationalization
        label_manager = LabelManager()
        initial_message = label_manager.settings_api_key_message
        return cls._create_dialog(
            initial_message=initial_message,
            main_window=main_window,
        )
