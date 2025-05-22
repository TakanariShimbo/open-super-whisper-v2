"""
Status Indicator Factory

This module provides a factory for creating status indicator instances,
following the factory design pattern to centralize view creation logic.
"""

from PyQt6.QtWidgets import QWidget

from ..widgets.status_indicator import StatusIndicatorWindow


class StatusIndicatorFactory:
    """
    Factory class for creating status indicator instances.

    This class provides methods to create properly configured status indicator
    view instances, following the MVC pattern.
    """

    @staticmethod
    def create_indicator(main_window: QWidget | None = None) -> StatusIndicatorWindow:
        """
        Create a status indicator instance.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget for the status indicator, by default None

        Returns
        -------
        StatusIndicatorWindow
            The created status indicator view
        """
        indicator = StatusIndicatorWindow(main_window=main_window)

        return indicator
