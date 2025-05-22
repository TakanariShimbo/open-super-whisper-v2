"""
API Key Dialog Factory

This module provides a factory for creating API key dialog instances,
following the factory design pattern to centralize dialog creation logic.
"""

from PyQt6.QtWidgets import QWidget

from ..dialogs.api_key_dialog import APIKeyDialog


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
        initial_message = "Welcome to Open Super Whisper! Please enter your OpenAI API key to get started."
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
        initial_message = "Update your API key or enter a new one if needed."
        return cls._create_dialog(
            initial_message=initial_message,
            main_window=main_window,
        )
