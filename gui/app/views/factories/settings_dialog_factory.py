"""
Settings Dialog Factory

This module provides a factory for creating settings dialog instances,
following the factory design pattern to centralize dialog creation logic.
"""

from PyQt6.QtWidgets import QWidget

from ..dialogs.settings_dialog import SettingsDialog


class SettingsDialogFactory:
    """
    Factory class for creating settings dialog instances.

    This class provides methods to create properly configured settings
    dialog instances with their controllers, following the MVC pattern.
    """

    @staticmethod
    def create_dialog(main_window: QWidget | None = None) -> SettingsDialog:
        """
        Create a settings dialog instance.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget for the dialog, by default None

        Returns
        -------
        SettingsDialog
            The created settings dialog instance
        """
        dialog = SettingsDialog(main_window=main_window)

        return dialog
