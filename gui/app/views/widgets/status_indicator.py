"""
Status Indicator Window

This module provides a floating window that displays the current status of recording.
It is designed to work with the MVC architecture and single responsibility principle.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPalette, QColor, QShowEvent

from ...managers.settings_manager import SettingsManager
from ...controllers.widgets.status_indicator_controller import StatusIndicatorController


class LabelManager:
    """
    Manages application labels for internationalization support in Status Indicator.
    """

    ALL_LABELS = {
        "English": {
            # Status Labels
            "status_recording": "Recording...",
            "status_processing": "Processing...",
            "status_completed": "Completed!",
            "status_cancelled": "Cancelled!",
        },
        "Japanese": {
            # Status Labels
            "status_recording": "Recording...",
            "status_processing": "Processing...",
            "status_completed": "Completed!",
            "status_cancelled": "Cancelled!",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # Load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # Set labels based on language
        self._labels = self.ALL_LABELS[language]

    # Status Labels
    @property
    def status_recording(self) -> str:
        return self._labels["status_recording"]

    @property
    def status_processing(self) -> str:
        return self._labels["status_processing"]

    @property
    def status_completed(self) -> str:
        return self._labels["status_completed"]

    @property
    def status_cancelled(self) -> str:
        return self._labels["status_cancelled"]


class StatusIndicatorWindow(QWidget):
    """
    Floating indicator window for recording, processing, and completion status.

    This window shows the current status of recording, transcription,
    and provides visual feedback to the user.
    """

    # Status constants - these should match the model
    _MODE_RECORDING = 1
    _MODE_PROCESSING = 2
    _MODE_COMPLETED = 3
    _MODE_CANCELLED = 4

    def __init__(self, main_window: QWidget | None = None) -> None:
        """
        Initialize the StatusIndicatorWindow.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget, by default None
        """
        super().__init__(
            parent=main_window,
            flags=Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
        )

        # Initialize label manager
        self._label_manager = LabelManager()

        # Create controller
        self._controller = StatusIndicatorController(status_indicator=self)

        # Set initial mode
        self._current_mode = self._MODE_RECORDING

        # Init UI
        self._init_ui()

        # Position window in bottom right corner of screen
        self._update_position()

        # Connect controller signals
        self._connect_controller_signals()

    #
    # UI Setup
    #
    def _init_ui(self) -> None:
        """
        Initialize user interface components.
        """
        # Set window properties
        self.setMinimumSize(120, 60)
        self.setMaximumSize(200, 100)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create frame for background
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setLineWidth(1)
        frame.setMidLineWidth(0)

        # Set background color
        palette = frame.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30, 220))
        frame.setAutoFillBackground(True)
        frame.setPalette(palette)

        # Frame layout
        frame_layout = QVBoxLayout(frame)

        # Status text
        self.status_label = QLabel(self._label_manager.status_recording)
        self.status_label.setStyleSheet("color: #ff5f5f; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Timer text
        self.timer_label = QLabel("")
        self.timer_label.setStyleSheet("color: white;")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add to layout
        frame_layout.addWidget(self.status_label)
        frame_layout.addWidget(self.timer_label)

        # Add frame to main layout
        main_layout.addWidget(frame)

        # Update indicator based on initial mode
        self._update_indicator()

    def _update_position(self) -> None:
        """
        Update window position to bottom right corner of screen.
        """
        desktop = self.screen().availableGeometry()
        self.move(desktop.width() - self.width() - 20, desktop.height() - self.height() - 60)

    def _update_indicator(self) -> None:
        """
        Update the indicator visuals based on current mode.
        """
        if self._current_mode == self._MODE_RECORDING:
            self.status_label.setText(self._label_manager.status_recording)
            self.status_label.setStyleSheet("color: #ff5f5f; font-weight: bold;")
        elif self._current_mode == self._MODE_PROCESSING:
            self.status_label.setText(self._label_manager.status_processing)
            self.status_label.setStyleSheet("color: #bbbbbb; font-weight: bold;")
            self.timer_label.setText("")
        elif self._current_mode == self._MODE_COMPLETED:
            self.status_label.setText(self._label_manager.status_completed)
            self.status_label.setStyleSheet("color: #5fff5f; font-weight: bold;")
            self.timer_label.setText("")
        elif self._current_mode == self._MODE_CANCELLED:
            self.status_label.setText(self._label_manager.status_cancelled)
            self.status_label.setStyleSheet("color: #bbbbbb; font-weight: bold;")
            self.timer_label.setText("")

    #
    # Controller Signals
    #
    def _connect_controller_signals(self) -> None:
        """
        Connect signals from controller to view methods.
        """
        # Connect controller signals to update view
        self._controller.mode_changed.connect(self._handle_mode_changed)
        self._controller.timer_updated.connect(self._handle_timer_updated)
        self._controller.visibility_changed.connect(self._handle_visibility_changed)

    #
    # Controller Events
    #
    @pyqtSlot(int)
    def _handle_mode_changed(self, mode: int) -> None:
        """
        Handle mode changes.

        Parameters
        ----------
        mode : int
            Mode constant (_MODE_RECORDING, _MODE_PROCESSING, _MODE_COMPLETED, _MODE_CANCELLED)
        """
        if self._current_mode != mode:
            self._current_mode = mode
            self._update_indicator()

    @pyqtSlot(str)
    def _handle_timer_updated(self, time_str: str) -> None:
        """
        Handle timer updates.

        Parameters
        ----------
        time_str : str
            Time string to display (e.g. "00:15")
        """
        self.timer_label.setText(time_str)

    @pyqtSlot(bool)
    def _handle_visibility_changed(self, visible: bool) -> None:
        """
        Handle visibility changes.

        Parameters
        ----------
        visible : bool
            Whether the indicator should be visible
        """
        if visible:
            self.show()
        else:
            self.hide()

    #
    # Open/Close Events
    #
    def showEvent(self, event: QShowEvent) -> None:
        """
        Handle show event by updating position.

        Parameters
        ----------
        event : QShowEvent
            Show event
        """
        super().showEvent(event)
        self._update_position()

    #
    # Get Controller
    #
    def get_controller(self) -> StatusIndicatorController:
        """
        Get the controller associated with this view.

        Returns
        -------
        StatusIndicatorController
            The controller for this view
        """
        return self._controller
