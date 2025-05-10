"""
API Key Dialog View

This module provides the view component for API key input dialog.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal


class APIKeyDialog(QDialog):
    """
    Dialog for API key input.
    
    This class provides a user-friendly dialog for entering an API key
    with proper explanation and validation feedback.
    
    Signals
    -------
    api_key_entered : pyqtSignal
        Signal emitted when a valid API key is entered
    """
    
    # Signal emitted when API key is entered
    api_key_entered = pyqtSignal(str)
    
    def __init__(self, parent=None, initial_message=None, is_settings_mode=False):
        """
        Initialize the API Key Dialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        initial_message : str, optional
            Initial message to display as error/info, by default None
        is_settings_mode : bool, optional
            Whether the dialog is being used in settings mode, by default False
        """
        super().__init__(parent)
        
        # Store the mode
        self._is_settings_mode = is_settings_mode
        
        # Set window title based on mode
        if is_settings_mode:
            self.setWindowTitle("API Key Settings")
        else:
            self.setWindowTitle("API Key Required")
            
        self.setMinimumWidth(400)
        
        # Create UI components
        self._init_ui()
        
        # Set initial message if provided
        if initial_message:
            self.show_status_message(initial_message)
    
    def _init_ui(self):
        """
        Initialize the dialog UI components.
        """
        layout = QVBoxLayout()
        
        # Title label - different based on mode
        if self._is_settings_mode:
            title_label = QLabel("OpenAI API Key Settings")
        else:
            title_label = QLabel("OpenAI API Key Required")
            
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Help text - different based on mode
        if self._is_settings_mode:
            help_text = QLabel(
                "You can update your OpenAI API key here.\n\n"
                "A valid API key is required for the application to function correctly.\n"
                "Your key will be stored securely in your application settings."
            )
        else:
            help_text = QLabel(
                "To use Super Whisper, you need a valid OpenAI API key.\n\n"
                "If you don't have an API key:\n"
                "1. Create an account at https://platform.openai.com\n"
                "2. Navigate to API Keys section\n"
                "3. Create a new API key\n"
                "4. Copy and paste the key below"
            )
            
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        
        # API key input
        layout.addSpacing(10)
        
        # Input label - different based on mode
        if self._is_settings_mode:
            input_label = QLabel("Enter or update your OpenAI API key:")
        else:
            input_label = QLabel("Enter your OpenAI API key:")
            
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
        self._cancel_button.clicked.connect(self.reject)
        self._ok_button.clicked.connect(self._on_ok_clicked)
        self._api_key_input.returnPressed.connect(self._on_ok_clicked)
    
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
    
    def _on_ok_clicked(self):
        """
        Handle OK button click.
        
        This method emits the api_key_entered signal with the entered API key.
        """
        entered_api_key = self.get_entered_api_key()
        
        if not entered_api_key:
            self.show_status_message("API key cannot be empty")
            return
        
        # Emit the signal with the entered API key
        self.api_key_entered.emit(entered_api_key)
    
    def get_entered_api_key(self):
        """
        Get the entered API key.
        
        Returns
        -------
        str
            The entered API key
        """
        return self._api_key_input.text().strip()
    
    def show_status_message(self, message):
        """
        Display a message in the status label.
        
        Parameters
        ----------
        message : str
            The message to display
        """
        self._status_label.setText(message)
        self._status_label.setVisible(True)
