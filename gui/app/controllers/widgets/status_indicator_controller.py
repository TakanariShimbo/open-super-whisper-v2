"""
Status Indicator Controller

This module provides the controller component for the status indicator window,
following the MVC architecture.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from ...models.widgets.status_indicator_model import StatusIndicatorModel


class StatusIndicatorController(QObject):
    """
    Controller for the status indicator.

    This class handles interactions between the status indicator model
    and provides methods for the view to control the status indicator.
    It serves as a mediator between the model and the view.
    """

    # Define signals for view communication
    mode_changed = pyqtSignal(int)  # mode
    timer_updated = pyqtSignal(str)  # time_string
    visibility_changed = pyqtSignal(bool)  # visible

    def __init__(self, status_indicator: QObject | None = None) -> None:
        """
        Initialize the controller.

        Parameters
        ----------
        status_indicator : QObject, optional
            Parent object, by default None
        """
        super().__init__(parent=status_indicator)

        # Create model
        self._model = StatusIndicatorModel(status_indicator=status_indicator)

        # Connect model signals to controller handlers
        self._connect_model_signals()

    def _connect_model_signals(self) -> None:
        """
        Connect signals from the model to controller handlers.
        """
        # Connect model signals to controller handlers
        self._model.mode_changed.connect(self._handle_mode_changed)
        self._model.timer_updated.connect(self._handle_timer_updated)
        self._model.visibility_changed.connect(self._handle_visibility_changed)

    @pyqtSlot(int)
    def _handle_mode_changed(self, mode: int) -> None:
        """
        Handle mode changes.

        Parameters
        ----------
        mode : int
            The new mode value
        """
        # Forward the mode change to views
        self.mode_changed.emit(mode)

    @pyqtSlot(str)
    def _handle_timer_updated(self, time_str: str) -> None:
        """
        Handle timer updates.

        Parameters
        ----------
        time_str : str
            The new time string
        """
        # Forward the timer update to views
        self.timer_updated.emit(time_str)

    @pyqtSlot(bool)
    def _handle_visibility_changed(self, visible: bool) -> None:
        """
        Handle visibility changes.

        Parameters
        ----------
        visible : bool
            Whether the indicator should be visible
        """
        self.visibility_changed.emit(visible)

    def start_recording(self) -> None:
        """
        Start recording mode and timer.
        """
        self._model.start_recording()

    def start_processing(self) -> None:
        """
        Start processing mode.
        """
        self._model.start_processing()

    def complete_processing(self) -> None:
        """
        Set completion mode.
        """
        self._model.complete_processing()

    def cancel_processing(self) -> None:
        """
        Set cancelled mode.
        """
        self._model.cancel_processing()
