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

from ...managers.settings_manager import SettingsManager
from ...controllers.dialogs.hotkey_dialog_controller import HotkeyDialogController


class LabelManager:
    """
    Manages application labels for internationalization support.
    """

    ALL_LABELS = {
        "English": {
            "window_title": "Hotkey Settings",
            "description": "Set a global hotkey combination for this instruction set.",
            "hotkey_label": "Hotkey:",
            "placeholder_click": "Click to capture keys",
            "placeholder_capture": "Press keys to capture hotkey...",
            "button_capture": "Capture",
            "button_stop_capturing": "Stop Capturing",
            "button_clear": "Clear",
            "tips_text": ("Tips:\n" "• Click 'Capture' and press keys to set a hotkey\n" "• Examples: ctrl+shift+r, alt+a, ctrl+alt+s"),
            "error_title": "Hotkey Validation Error",
        },
        "Japanese": {
            "window_title": "ホットキー設定",
            "description": "このインストラクションセットのためのグローバルホットキーを設定してください。",
            "hotkey_label": "ホットキー:",
            "placeholder_click": "クリックしてキーを取得",
            "placeholder_capture": "ホットキーとして登録するキーを押してください...",
            "button_capture": "キャプチャ",
            "button_stop_capturing": "ストップ",
            "button_clear": "クリア",
            "tips_text": ("ヒント:\n" "・『キャプチャ』をクリックしてキーを押すとホットキーを設定できます\n" "・例: ctrl+shift+r, alt+a, ctrl+alt+s"),
            "error_title": "ホットキー検証エラー",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # set labels based on language
        self._labels = self.ALL_LABELS[language]

    @property
    def window_title(self) -> str:
        return self._labels["window_title"]

    @property
    def description(self) -> str:
        return self._labels["description"]

    @property
    def hotkey_label(self) -> str:
        return self._labels["hotkey_label"]

    @property
    def placeholder_click(self) -> str:
        return self._labels["placeholder_click"]

    @property
    def placeholder_capture(self) -> str:
        return self._labels["placeholder_capture"]

    @property
    def button_capture(self) -> str:
        return self._labels["button_capture"]

    @property
    def button_stop_capturing(self) -> str:
        return self._labels["button_stop_capturing"]

    @property
    def button_clear(self) -> str:
        return self._labels["button_clear"]

    @property
    def tips_text(self) -> str:
        return self._labels["tips_text"]

    @property
    def error_title(self) -> str:
        return self._labels["error_title"]


class HotkeyDialog(QDialog):
    """
    Dialog for setting global hotkeys.

    This dialog allows users to define a custom hotkey combination
    for various actions in the application. It uses an advanced key
    capture method for accurate hotkey detection.
    """

    def __init__(
        self,
        current_hotkey: str = "",
        instruction_dialog: QWidget | None = None,
    ) -> None:
        """
        Initialize the HotkeyDialog.

        Parameters
        ----------
        current_hotkey : str, optional
            Current hotkey string, by default ""
        instruction_dialog : QWidget, optional
            Parent widget, by default None

        """
        super().__init__(parent=instruction_dialog)

        # Initialize label manager
        self._label_manager = LabelManager()

        # Create controller
        self._controller = HotkeyDialogController(
            current_hotkey=current_hotkey,
            hotkey_dialog=self,
        )

        # Set up UI
        self._init_ui()

        # Connect controller signals
        self._connect_controller_signals()

        # Timer for continuous key capture
        self._capture_timer = QTimer(self)
        self._capture_timer.setInterval(100)  # 100ms interval
        self._capture_timer.timeout.connect(self._on_capture_timer)

    #
    # UI Setup
    #
    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Set dialog properties
        self.setWindowTitle(self._label_manager.window_title)
        self.setMinimumWidth(400)

        # Create layout
        layout = QVBoxLayout(self)

        # Create grid for form
        form_layout = QGridLayout()

        # Add description
        description = QLabel(self._label_manager.description)
        description.setWordWrap(True)

        # Create hotkey display area
        hotkey_label = QLabel(self._label_manager.hotkey_label)

        # Hotkey display field (read-only)
        self._hotkey_display = QLineEdit(self._controller.get_hotkey())
        self._hotkey_display.setReadOnly(True)
        self._hotkey_display.setPlaceholderText(self._label_manager.placeholder_click)

        # Styling for the hotkey display when in capture mode
        self._normal_style = self._hotkey_display.styleSheet()
        self._capture_style = "QLineEdit { background-color: #f0f0f0; border: 2px solid #3498db; }"

        # Container for capture button and reset button
        button_container = QHBoxLayout()

        # Capture button
        self._capture_button = QPushButton(self._label_manager.button_capture)
        self._capture_button.setCheckable(True)
        self._capture_button.clicked.connect(self._on_toggle_capture)
        button_container.addWidget(self._capture_button)

        # Reset button
        reset_button = QPushButton(self._label_manager.button_clear)
        reset_button.clicked.connect(self._on_click_reset)
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
        tips_label = QLabel(self._label_manager.tips_text)
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

    #
    # Controller Signals
    #
    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller.
        """
        self._controller.hotkey_changed.connect(self._handle_hotkey_changed)
        self._controller.hotkey_captured.connect(self._handle_hotkey_captured)
        self._controller.validation_error.connect(self._handle_validation_error)

    #
    # Controller Events
    #
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
            self._label_manager.error_title,
            message,
        )

    #
    # UI Events
    #
    def _start_capture_mode(self) -> None:
        """
        Start key capture mode.
        """
        # Update button text
        self._capture_button.setText(self._label_manager.button_stop_capturing)

        # Apply capture style to input field
        self._hotkey_display.setStyleSheet(self._capture_style)
        self._hotkey_display.setPlaceholderText(self._label_manager.placeholder_capture)

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
        self._capture_button.setText(self._label_manager.button_capture)

        # Restore normal style
        self._hotkey_display.setStyleSheet(self._normal_style)
        self._hotkey_display.setPlaceholderText(self._label_manager.placeholder_click)

        # Stop key capture in controller
        self._controller.stop_capturing()

        # Stop capture timer
        self._capture_timer.stop()

    @pyqtSlot(bool)
    def _on_toggle_capture(self, checked: bool) -> None:
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

    @pyqtSlot()
    def _on_capture_timer(self) -> None:
        """
        Handle capture timer tick.
        """
        # Capture current keys
        self._controller.capture_keys()

    @pyqtSlot()
    def _on_click_reset(self) -> None:
        """
        Handle reset button click.
        """
        # Stop capture mode if active
        if self._capture_button.isChecked():
            self._stop_capture_mode()

        # Reset hotkey in controller
        self._controller.reset_hotkey()

    #
    # UI Events
    #

    def get_hotkey(self) -> str:
        """
        Get the hotkey string.

        Returns
        -------
        str
            The hotkey combination as a string.
        """
        return self._controller.get_hotkey()

    #
    # Open/Close Events
    #
    @pyqtSlot()
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

    @pyqtSlot()
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
