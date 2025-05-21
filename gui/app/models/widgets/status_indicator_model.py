"""
Status Indicator Model

This module provides the model component for the status indicator in the
Super Whisper application, following the MVC architecture.
"""

import time

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from ...managers.settings_manager import SettingsManager


class StatusIndicatorModel(QObject):
    """
    Model for the status indicator.

    This class manages the state of the status indicator and provides
    signals to notify of state changes.
    """

    # Status constants
    _MODE_RECORDING = 1
    _MODE_PROCESSING = 2
    _MODE_COMPLETED = 3
    _MODE_CANCELLED = 4

    # Signals
    mode_changed = pyqtSignal(int)  # mode
    timer_updated = pyqtSignal(str)  # time_string
    visibility_changed = pyqtSignal(bool)  # visible

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Initialize the model.

        Parameters
        ----------
        parent : QObject, optional
            Parent object, by default None
        """
        super().__init__(parent=parent)

        # Get settings manager
        self._settings_manager = SettingsManager.instance()

        # State variables
        self._mode = self._MODE_RECORDING
        self._visible = False
        self._recording_start_time = 0

        # Timer for recording time updates
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_timer)
        self._timer.setInterval(1000)  # Update every second

    def set_mode(self, mode: int) -> None:
        """
        Set the indicator mode.

        Parameters
        ----------
        mode : int
            Mode constant (_MODE_RECORDING, _MODE_PROCESSING, _MODE_COMPLETED, _MODE_CANCELLED)
        """
        if self._mode != mode:
            self._mode = mode
            self.mode_changed.emit(mode)

    def set_visible(self, visible: bool) -> None:
        """
        Set the indicator visibility.

        Parameters
        ----------
        visible : bool
            Whether the indicator should be visible
        """
        if self._visible == visible:
            return

        # Check if indicator should be visible based on settings
        indicator_visible_setting = self._settings_manager.get_indicator_visible()

        if indicator_visible_setting:
            self._visible = visible
            self.visibility_changed.emit(visible)

    def update_timer(self, elapsed_time: float | None = None) -> None:
        """
        Update the timer display.

        Parameters
        ----------
        elapsed_time : float | None, optional
            Elapsed time in seconds, by default calculates from recording start time
        """
        if elapsed_time is None and self._recording_start_time > 0:
            elapsed_time = time.time() - self._recording_start_time

        if elapsed_time is not None:
            elapsed = int(elapsed_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.timer_updated.emit(time_str)

    def _update_timer(self) -> None:
        """
        Update timer display based on elapsed recording time.
        """
        self.update_timer()

    def start_recording(self) -> None:
        """
        Start recording mode and timer.
        """
        self._recording_start_time = time.time()
        self.set_mode(mode=self._MODE_RECORDING)
        self.update_timer(elapsed_time=0)  # Reset timer display
        self._timer.start()  # Start timer updates
        self.set_visible(visible=True)  # Show indicator

    def start_processing(self) -> None:
        """
        Start processing mode.
        """
        self._timer.stop()  # Stop timer updates
        self.set_mode(mode=self._MODE_PROCESSING)
        self.set_visible(visible=True)  # Ensure indicator is visible

    def complete_processing(self) -> None:
        """
        Set completion mode.
        """
        self._timer.stop()  # Stop timer updates
        self.set_mode(mode=self._MODE_COMPLETED)
        # Keep indicator visible for a short time
        QTimer.singleShot(3000, lambda: self.set_visible(visible=False))

    def cancel_processing(self) -> None:
        """
        Set cancelled mode.
        """
        self._timer.stop()  # Stop timer updates
        self.set_mode(mode=self._MODE_CANCELLED)
        # Keep indicator visible for a short time
        QTimer.singleShot(3000, lambda: self.set_visible(visible=False))
