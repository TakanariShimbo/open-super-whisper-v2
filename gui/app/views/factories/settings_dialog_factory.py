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
    def create_dialog(parent: QWidget | None = None) -> SettingsDialog:
        """
        Create a settings dialog instance.

        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None

        Returns
        -------
        SettingsDialog
            The created settings dialog instance
        """
        # Create a settings dialog with the controller
        dialog = SettingsDialog(parent=parent)

        return dialog
