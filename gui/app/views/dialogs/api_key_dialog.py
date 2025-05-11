"""
API Key Dialog View

This module provides the view component for API key input dialog.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QCloseEvent

from ...controllers.dialogs.api_key_controller import APIKeyController


class APIKeyDialog(QDialog):
    """
    Dialog for API key input.
    
    This class provides a user-friendly dialog for entering an API key
    with proper explanation and validation feedback.
    """
    
    def __init__(self, parent=None, initial_message=None):
        """
        Initialize the API Key Dialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        initial_message : str, optional
            Initial message to display as error/info, by default None
        """
        super().__init__(parent)
        
        # Create controller
        self._controller = APIKeyController()
        
        # Create UI components
        self._init_ui()
        
        # Connect controller signals
        self._connect_controller_signals()
        
        # Set initial message if provided
        if initial_message:
            self.show_status_message(initial_message)
        
        # Initialize API key field
        current_api_key = self._controller.get_api_key()
        if current_api_key:
            self._api_key_input.setText(current_api_key)
    
    def _init_ui(self):
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
        input_layout.addWidget(self._api_key_input, 1)  # Use stretch factor 1
        
        # Toggle visibility button
        self._toggle_button = QPushButton("👁️")
        self._toggle_button.setToolTip("Show/Hide API Key")
        self._toggle_button.setFixedWidth(30)  # Fixed width for the button
        self._toggle_button.setCheckable(True)  # Make it a toggle button
        self._toggle_button.setChecked(False)  # Initially not checked
        self._toggle_button.clicked.connect(self._toggle_key_visibility)
        input_layout.addWidget(self._toggle_button)
        
        # Add the input layout to the main layout
        layout.addLayout(input_layout)
        
        # Status label (initially hidden)
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: red;")
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self._cancel_button = QPushButton("Cancel")
        self._ok_button = QPushButton("OK")
        self._ok_button.setDefault(True)
        
        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._ok_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self._cancel_button.clicked.connect(self._on_cancel_clicked)
        self._ok_button.clicked.connect(self._on_ok_clicked)
        self._api_key_input.returnPressed.connect(self._on_ok_clicked)
    
    def _connect_controller_signals(self):
        """
        Connect signals from the controller.
        """
        # Connect controller signals to view methods
        self._controller.api_key_validated.connect(self._on_api_key_validated)
        self._controller.api_key_invalid.connect(self._on_api_key_invalid)
    
    def _toggle_key_visibility(self):
        """
        Toggle the visibility of the API key in the input field.
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
    
    @pyqtSlot()
    def _on_ok_clicked(self):
        """
        Handle OK button click.
        """
        entered_api_key = self.get_entered_api_key()
        
        if not entered_api_key:
            self.show_status_message("API key cannot be empty")
            return
        
        # Use controller to validate the key
        self._controller.validate_key(entered_api_key)
    
    @pyqtSlot()
    def _on_cancel_clicked(self):
        """
        Handle Cancel button click.
        """
        # Restore original state
        self._controller.cancel()
        
        # Reject the dialog
        super().reject()
    
    @pyqtSlot()
    def _on_api_key_validated(self) -> None:
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
    def _on_api_key_invalid(self) -> None:
        """
        Handle failed API key validation.
        
        Parameters
        ----------
        api_key : str
            The invalid API key
        """
        self.show_status_message("Invalid API key. Please check and try again.")
    
    def get_entered_api_key(self):
        """
        Get the entered API key.
        
        Returns
        -------
        str
            The entered API key
        """
        return self._api_key_input.text().strip()
    
    def show_status_message(self, message: str) -> None:
        """
        Display a message in the status label.
        
        Parameters
        ----------
        message : str
            The message to display
        """
        self._status_label.setText(message)
        self._status_label.setVisible(True)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle dialog close event.
        
        Restore original settings when dialog is closed without accepting.
        
        Parameters
        ----------
        event : QCloseEvent
            Close event
        """
        # Restore original settings
        self._controller.cancel()
        
        # Call parent class method
        super().closeEvent(event)
