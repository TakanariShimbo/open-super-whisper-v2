"""
Hotkey Dialog View

This module provides the view component for setting hotkeys in the Open Super Whisper application.
It integrates the MVC components of the hotkey dialog.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
    QGridLayout,
    QMessageBox,
    QHBoxLayout,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QCloseEvent, QShowEvent

from ...controllers.dialogs.hotkey_dialog_controller import HotkeyDialogController


class HotkeyDialog(QDialog):
    """
    Dialog for setting global hotkeys.

    This dialog allows users to define a custom hotkey combination
    for various actions in the application. It uses an advanced key
    capture method for accurate hotkey detection.
    """

    def __init__(self, current_hotkey: str = "", parent: QWidget | None = None) -> None:
        """
        Initialize the HotkeyDialog.

        Parameters
        ----------
        current_hotkey : str, optional
            Current hotkey string, by default ""
        parent : QWidget, optional
            Parent widget, by default None

        """
        super().__init__(parent=parent)

        # Create controller
        self._controller = HotkeyDialogController(current_hotkey=current_hotkey)

        # Set up UI
        self._init_ui()

        # Connect controller signals
        self._connect_controller_signals()

        # Timer for continuous key capture
        self._capture_timer = QTimer(self)
        self._capture_timer.setInterval(100)  # 100ms interval
        self._capture_timer.timeout.connect(self._on_capture_timer)

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Set dialog properties
        self.setWindowTitle("Hotkey Settings")
        self.setMinimumWidth(400)

        # Create layout
        layout = QVBoxLayout(self)

        # Create grid for form
        form_layout = QGridLayout()

        # Add description
        description = QLabel("Set a global hotkey combination for this action.")
        description.setWordWrap(True)

        # Create hotkey display area
        hotkey_label = QLabel("Hotkey:")

        # Hotkey display field (read-only)
        self._hotkey_display = QLineEdit(self._controller.get_hotkey())
        self._hotkey_display.setReadOnly(True)
        self._hotkey_display.setPlaceholderText("Click to capture keys")

        # Styling for the hotkey display when in capture mode
        self._normal_style = self._hotkey_display.styleSheet()
        self._capture_style = "QLineEdit { background-color: #f0f0f0; border: 2px solid #3498db; }"

        # Container for capture button and reset button
        button_container = QHBoxLayout()

        # Capture button
        self._capture_button = QPushButton("Capture")
        self._capture_button.setCheckable(True)
        self._capture_button.clicked.connect(self._on_capture_toggled)
        button_container.addWidget(self._capture_button)

        # Reset button
        reset_button = QPushButton("Clear")
        reset_button.clicked.connect(self._on_reset_clicked)
        button_container.addWidget(reset_button)

        # Add to grid layout
        form_layout.addWidget(description, 0, 0, 1, 2)
        form_layout.addWidget(hotkey_label, 1, 0)
        form_layout.addWidget(self._hotkey_display, 1, 1)
        form_layout.addLayout(button_container, 2, 1, Qt.AlignmentFlag.AlignRight)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        # Add hotkey examples and tips
        tips_label = QLabel("Tips:\n• Click 'Capture' and press keys to set a hotkey\n• Examples: ctrl+shift+r, alt+a, ctrl+alt+s")
        tips_label.setWordWrap(True)

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self._on_reject)

        # Add components to main layout
        layout.addLayout(form_layout)
        layout.addWidget(separator)
        layout.addWidget(tips_label)
        layout.addWidget(button_box)

    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller.
        """
        self._controller.hotkey_changed.connect(self._handle_hotkey_changed)
        self._controller.hotkey_captured.connect(self._handle_hotkey_captured)
        self._controller.validation_error.connect(self._handle_validation_error)

    @pyqtSlot(bool)
    def _on_capture_toggled(self, checked: bool) -> None:
        """
        Handle capture button toggle.

        Parameters
        ----------
        checked : bool
            Whether the button is checked
        """
        if checked:
            # Start capture mode
            self._start_capture_mode()
        else:
            # Stop capture mode
            self._stop_capture_mode()

    def _start_capture_mode(self) -> None:
        """
        Start key capture mode.
        """
        # Update button text
        self._capture_button.setText("Stop Capturing")

        # Apply capture style to input field
        self._hotkey_display.setStyleSheet(self._capture_style)
        self._hotkey_display.setPlaceholderText("Press keys to capture hotkey...")

        # Give focus to the display field
        self._hotkey_display.setFocus()

        # Start key capture in controller
        self._controller.start_capturing()

        # Start capture timer
        self._capture_timer.start()

    def _stop_capture_mode(self) -> None:
        """
        Stop key capture mode.
        """
        # Update button state and text
        self._capture_button.setChecked(False)
        self._capture_button.setText("Capture")

        # Restore normal style
        self._hotkey_display.setStyleSheet(self._normal_style)
        self._hotkey_display.setPlaceholderText("Click to capture keys")

        # Stop key capture in controller
        self._controller.stop_capturing()

        # Stop capture timer
        self._capture_timer.stop()

    @pyqtSlot()
    def _on_capture_timer(self) -> None:
        """
        Handle capture timer tick.
        """
        # Capture current keys
        self._controller.capture_keys()

    @pyqtSlot()
    def _on_reset_clicked(self) -> None:
        """
        Handle reset button click.
        """
        # Stop capture mode if active
        if self._capture_button.isChecked():
            self._stop_capture_mode()

        # Reset hotkey in controller
        self._controller.reset_hotkey()

    @pyqtSlot(str)
    def _handle_hotkey_changed(self, hotkey: str) -> None:
        """
        Handle hotkey changed event from the controller.

        Parameters
        ----------
        hotkey : str
            The new hotkey value
        """
        self._hotkey_display.setText(hotkey)

    @pyqtSlot(str)
    def _handle_hotkey_captured(self, hotkey: str) -> None:
        """
        Handle hotkey captured event from the controller.

        Parameters
        ----------
        hotkey : str
            The captured hotkey
        """
        # Just update the display (controller already updated the model)
        self._hotkey_display.setText(hotkey)

    @pyqtSlot(str)
    def _handle_validation_error(self, message: str) -> None:
        """
        Handle validation error event from the controller.

        Parameters
        ----------
        message : str
            Error message
        """
        QMessageBox.warning(
            self,
            "Hotkey Validation Error",
            message,
        )

    def _on_accept(self) -> None:
        """
        Handle dialog acceptance.
        """
        # Stop capture mode if active
        if self._capture_button.isChecked():
            self._stop_capture_mode()

        # Validate hotkey before accepting
        if not self._controller.validate_hotkey():
            return

        # Save the validated hotkey
        self._controller.save()

        # Accept the dialog
        super().accept()

    def _on_reject(self) -> None:
        """
        Handle dialog rejection.
        """
        # Stop capture mode if active
        if self._capture_button.isChecked():
            self._stop_capture_mode()

        # Tell controller to restore original hotkey
        self._controller.cancel()

        # Reject the dialog
        super().reject()

    def get_hotkey(self) -> str:
        """
        Get the hotkey string.

        Returns
        -------
        str
            The hotkey combination as a string.
        """
        return self._controller.get_hotkey()

    def showEvent(self, event: QShowEvent) -> None:
        """
        Handle dialog show event.

        Parameters
        ----------
        event : QShowEvent
            Show event
        """
        # Call parent class method first
        super().showEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle dialog close event.

        Parameters
        ----------
        event : QCloseEvent
            Close event
        """
        # Stop capture mode if active
        if self._capture_button.isChecked():
            self._stop_capture_mode()

        # Cancel changes
        self._controller.cancel()

        # Call parent class method
        super().closeEvent(event)
