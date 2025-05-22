"""
Hotkey Dialog Factory

This module provides a factory for creating hotkey dialog instances,
following the factory design pattern to centralize dialog creation logic.
"""

from PyQt6.QtWidgets import QWidget

from ..dialogs.hotkey_dialog import HotkeyDialog


class HotkeyDialogFactory:
    """
    Factory class for creating hotkey dialog instances.

    This class provides methods to create properly configured hotkey
    dialog instances with their controllers, following the MVC pattern.
    """

    @staticmethod
    def create_dialog(
        current_hotkey: str = "",
        instruction_dialog: QWidget | None = None,
    ) -> HotkeyDialog:
        """
        Create a hotkey dialog instance.

        Parameters
        ----------
        current_hotkey : str, optional
            Current hotkey value, by default ""
        instruction_dialog : QWidget, optional
            Parent widget for the dialog, by default None

        Returns
        -------
        HotkeyDialog
            The created hotkey dialog instance
        """
        dialog = HotkeyDialog(
            current_hotkey=current_hotkey,
            instruction_dialog=instruction_dialog,
        )

        return dialog
