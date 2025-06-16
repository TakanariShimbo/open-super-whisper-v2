"""
API Key Dialog View

This module provides the view component for API key input dialog.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QDialogButtonBox, QLabel, QLineEdit
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QCloseEvent, QShowEvent

from ...managers.settings_manager import SettingsManager
from ...controllers.dialogs.api_key_dialog_controller import APIKeyDialogController


class LabelManager:
    """
    Manages application labels for internationalization support.
    """

    ALL_LABELS = {
        "English": {
            "window_title": "API Key",
            "title_label": "API Key Settings",
            "help_text": (
                "To use Open Super Whisper, you need a valid OpenAI API key.\n\n"
                "1. Create an account at https://platform.openai.com\n"
                "2. Navigate to API Keys section\n"
                "3. Create a new API key\n"
                "4. Copy and paste the key below"
            ),
            "openai_api_key_input_label": "OpenAI API key:",
            "openai_api_key_input_placeholder": "sk-...",
            "error_invalid_openai_api_key": "Invalid OpenAI API key. Please check and try again.",
            "error_empty_openai_api_key": "OpenAI API key cannot be empty",
            "tooltip_show_hide": "Show/Hide API Key",
            "tooltip_hide": "Hide API Key",
            "tooltip_show": "Show API Key",
        },
        "Japanese": {
            "window_title": "APIキー",
            "title_label": "API キー設定",
            "help_text": (
                "Open Super Whisperを利用するには有効なOpenAI APIキーが必要です。\n\n"
                "1. https://platform.openai.com でアカウントを作成\n"
                "2. API Keysセクションに移動\n"
                "3. 新しいAPIキーを作成\n"
                "4. 下の欄にキーをコピー＆ペースト"
            ),
            "openai_api_key_input_label": "OpenAI APIキー:",
            "openai_api_key_input_placeholder": "sk-...",
            "error_invalid_openai_api_key": "無効なOpenAI APIキーです。ご確認の上、再度お試しください。",
            "error_empty_openai_api_key": "OpenAI APIキーを入力してください",
            "tooltip_show_hide": "APIキーの表示/非表示",
            "tooltip_hide": "APIキーを非表示",
            "tooltip_show": "APIキーを表示",
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
    def title_label(self) -> str:
        return self._labels["title_label"]

    @property
    def help_text(self) -> str:
        return self._labels["help_text"]

    @property
    def openai_api_key_input_label(self) -> str:
        return self._labels["openai_api_key_input_label"]

    @property
    def openai_api_key_input_placeholder(self) -> str:
        return self._labels["openai_api_key_input_placeholder"]

    @property
    def error_invalid_openai_api_key(self) -> str:
        return self._labels["error_invalid_openai_api_key"]

    @property
    def error_empty_openai_api_key(self) -> str:
        return self._labels["error_empty_openai_api_key"]

    @property
    def tooltip_show_hide(self) -> str:
        return self._labels["tooltip_show_hide"]

    @property
    def tooltip_hide(self) -> str:
        return self._labels["tooltip_hide"]

    @property
    def tooltip_show(self) -> str:
        return self._labels["tooltip_show"]

class APIKeyDialog(QDialog):
    """
    Dialog for API key input.

    This class provides a user-friendly dialog for entering an API key
    with proper explanation and validation feedback.
    """

    def __init__(
        self,
        initial_message: str,
        main_window: QWidget | None = None,
    ) -> None:
        """
        Initialize the API Key Dialog.

        Parameters
        ----------
        initial_message : str
            Initial message to display as error/info
        main_window : QWidget, optional
            Parent widget, by default None
        """
        super().__init__(parent=main_window)

        # Initialize label manager
        self._label_manager = LabelManager()

        # Create controller
        self._controller = APIKeyDialogController(api_key_dialog=self)

        # Track hotkey state
        self._hotkeys_disabled = False

        # Create UI components
        self._init_ui()

        # Connect controller signals
        self._connect_controller_signals()

        # Set initial message if provided
        if initial_message:
            self._show_status_message(message=initial_message)

        # Initialize API key field
        current_openai_api_key = self._controller.get_openai_api_key()
        if current_openai_api_key:
            self._openai_api_key_input.setText(current_openai_api_key)

    def _show_status_message(self, message: str) -> None:
        """
        Display a message in the status label.

        Parameters
        ----------
        message : str
            The message to display
        """
        self._status_label.setText(message)
        self._status_label.setVisible(True)

    #
    # UI Setup
    #
    def _init_ui(self) -> None:
        """
        Initialize the dialog UI components.
        """
        # Set window title based on mode
        self.setWindowTitle(self._label_manager.window_title)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Title label
        title_label = QLabel(self._label_manager.title_label)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)

        # Help text
        help_text = QLabel(self._label_manager.help_text)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # API key input
        layout.addSpacing(10)

        # Input label
        input_label = QLabel(self._label_manager.openai_api_key_input_label)
        layout.addWidget(input_label)

        # Create a horizontal layout for input field and toggle button
        input_layout = QHBoxLayout()

        # API key input field
        self._openai_api_key_input = QLineEdit()
        self._openai_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._openai_api_key_input.setPlaceholderText(self._label_manager.openai_api_key_input_placeholder)
        self._openai_api_key_input.returnPressed.connect(self._on_accept)
        input_layout.addWidget(self._openai_api_key_input, 1)  # Use stretch factor 1

        # Toggle visibility button
        self._toggle_button = QPushButton("👁️")
        self._toggle_button.setToolTip(self._label_manager.tooltip_show_hide)
        self._toggle_button.setFixedWidth(30)  # Fixed width for the button
        self._toggle_button.setCheckable(True)  # Make it a toggle button
        self._toggle_button.setChecked(False)  # Initially not checked
        self._toggle_button.clicked.connect(self._on_toggle_key_visibility)
        input_layout.addWidget(self._toggle_button)

        # Add the input layout to the main layout
        layout.addLayout(input_layout)

        # Status label (initially hidden)
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: red;")
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self._on_reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    #
    # Controller Signals
    #
    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller.
        """
        # Connect controller signals to view methods
        self._controller.openai_api_key_validated.connect(self._handle_openai_api_key_validated)
        self._controller.openai_api_key_invalid.connect(self._handle_openai_api_key_invalid)

    #
    # Controller Events
    #
    @pyqtSlot()
    def _handle_openai_api_key_validated(self) -> None:
        """
        Handle successful OpenAI API key validation.

        Parameters
        ----------
        openai_api_key : str
            The validated OpenAI API key
        """
        # Restore hotkeys
        self._restore_hotkeys()

        # Save the valid OpenAI API key
        self._controller.save_openai_api_key()

        # Accept the dialog
        super().accept()

    @pyqtSlot()
    def _handle_openai_api_key_invalid(self) -> None:
        """
        Handle failed OpenAI API key validation.

        Parameters
        ----------
        openai_api_key : str
            The invalid OpenAI API key
        """
        self._show_status_message(message=self._label_manager.error_invalid_openai_api_key)

    #
    # UI Events
    #
    @pyqtSlot()
    def _on_toggle_key_visibility(self) -> None:
        """
        Handle key visibility toggle.
        """
        if self._toggle_button.isChecked():
            # Show API key
            self._openai_api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self._toggle_button.setText("🔒")
            self._toggle_button.setToolTip(self._label_manager.tooltip_hide)
        else:
            # Hide API key
            self._openai_api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self._toggle_button.setText("👁️")
            self._toggle_button.setToolTip(self._label_manager.tooltip_show)

    #
    # Open/Close Events
    #
    def _restore_hotkeys(self) -> None:
        """
        Restore hotkeys that were disabled.
        """
        if self._hotkeys_disabled:
            self._controller.start_listening()
            self._hotkeys_disabled = False

    def _get_entered_openai_api_key(self) -> str:
        """
        Get the entered OpenAI API key.

        Returns
        -------
        str
            The entered OpenAI API key
        """
        return self._openai_api_key_input.text().strip()

    @pyqtSlot()
    def _on_accept(self) -> None:
        """
        Handle dialog acceptance.
        """
        entered_openai_api_key = self._get_entered_openai_api_key()

        if not entered_openai_api_key:
            self._show_status_message(message=self._label_manager.error_empty_openai_api_key)
            return

        # Use controller to validate the key
        self._controller.validate_openai_api_key(openai_api_key=entered_openai_api_key)

    @pyqtSlot()
    def _on_reject(self) -> None:
        """
        Handle dialog rejection.
        """
        # Restore hotkeys
        self._restore_hotkeys()

        # Restore original state
        self._controller.cancel()

        # Reject the dialog
        super().reject()

    def showEvent(self, event: QShowEvent) -> None:
        """
        Handle dialog show event.

        Parameters
        ----------
        event : QShowEvent
            The show event
        """
        super().showEvent(event)

        # Disable hotkeys while dialog is open
        self._controller.stop_listening()
        self._hotkeys_disabled = True

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle dialog close event.

        Parameters
        ----------
        event : QCloseEvent
            Close event
        """
        # Restore hotkeys
        self._restore_hotkeys()

        # Restore original settings
        self._controller.cancel()

        # Call parent class method
        super().closeEvent(event)
