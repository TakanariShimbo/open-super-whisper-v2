"""
API Key Dialog View

This module provides the view component for API key input dialog.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QDialogButtonBox, QLabel, QLineEdit
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QCloseEvent

from ...controllers.dialogs.api_key_dialog_controller import APIKeyDialogController


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

        # Create controller
        self._controller = APIKeyDialogController(api_key_dialog=self)

        # Create UI components
        self._init_ui()

        # Connect controller signals
        self._connect_controller_signals()

        # Set initial message if provided
        if initial_message:
            self._show_status_message(message=initial_message)

        # Initialize API key field
        current_api_key = self._controller.get_api_key()
        if current_api_key:
            self._api_key_input.setText(current_api_key)

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
        self.setWindowTitle("API Key Settings")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("OpenAI API Key Settings")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)

        # Help text
        help_text = QLabel(
            "To use Open Super Whisper, you need a valid OpenAI API key.\n\n"
            "1. Create an account at https://platform.openai.com\n"
            "2. Navigate to API Keys section\n"
            "3. Create a new API key\n"
            "4. Copy and paste the key below"
        )

        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # API key input
        layout.addSpacing(10)

        # Input label
        input_label = QLabel("OpenAI API key:")

        layout.addWidget(input_label)

        # Create a horizontal layout for input field and toggle button
        input_layout = QHBoxLayout()

        # API key input field
        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_input.setPlaceholderText("sk-...")
        self._api_key_input.returnPressed.connect(self._on_accept)
        input_layout.addWidget(self._api_key_input, 1)  # Use stretch factor 1

        # Toggle visibility button
        self._toggle_button = QPushButton("👁️")
        self._toggle_button.setToolTip("Show/Hide API Key")
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
        self._controller.api_key_validated.connect(self._handle_api_key_validated)
        self._controller.api_key_invalid.connect(self._handle_api_key_invalid)

    #
    # Controller Events
    #
    @pyqtSlot()
    def _handle_api_key_validated(self) -> None:
        """
        Handle successful API key validation.

        Parameters
        ----------
        api_key : str
            The validated API key
        """
        # Save the valid API key
        self._controller.save_api_key()

        # Accept the dialog
        super().accept()

    @pyqtSlot()
    def _handle_api_key_invalid(self) -> None:
        """
        Handle failed API key validation.

        Parameters
        ----------
        api_key : str
            The invalid API key
        """
        self._show_status_message(message="Invalid API key. Please check and try again.")

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
            self._api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self._toggle_button.setText("🔒")
            self._toggle_button.setToolTip("Hide API Key")
        else:
            # Hide API key
            self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self._toggle_button.setText("👁️")
            self._toggle_button.setToolTip("Show API Key")

    #
    # Open/Close Events
    #
    def _get_entered_api_key(self) -> str:
        """
        Get the entered API key.

        Returns
        -------
        str
            The entered API key
        """
        return self._api_key_input.text().strip()

    @pyqtSlot()
    def _on_accept(self) -> None:
        """
        Handle dialog acceptance.
        """
        entered_api_key = self._get_entered_api_key()

        if not entered_api_key:
            self._show_status_message(message="API key cannot be empty")
            return

        # Use controller to validate the key
        self._controller.validate_api_key(api_key=entered_api_key)

    @pyqtSlot()
    def _on_reject(self) -> None:
        """
        Handle dialog rejection.
        """
        # Restore original state
        self._controller.cancel()

        # Reject the dialog
        super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle dialog close event.

        Parameters
        ----------
        event : QCloseEvent
            Close event
        """
        # Restore original settings
        self._controller.cancel()

        # Call parent class method
        super().closeEvent(event)
