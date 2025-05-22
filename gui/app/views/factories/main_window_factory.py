"""
Main Window Factory

This module provides a factory for creating main window instances,
following the factory design pattern to centralize window creation logic.
"""

from ..main_window import MainWindow


class MainWindowFactory:
    """
    Factory class for creating main window instances.

    This class provides methods to create properly configured main window instances
    with their controllers and models, following the MVC pattern.
    """

    @staticmethod
    def create_window() -> MainWindow:
        """
        Create a main window with associated controller and model.

        Returns
        -------
        MainWindow
            The created main window instance
        """
        window = MainWindow()

        return window
