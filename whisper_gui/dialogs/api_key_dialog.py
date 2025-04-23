"""
API Key Dialog

This module provides a dialog for setting and validating the OpenAI API key.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt

from whisper_core.transcriber import WhisperTranscriber
from whisper_gui.resources.labels import AppLabels


class APIKeyDialog(QDialog):
    """
    Dialog for managing the OpenAI API key.
    
    This dialog allows users to enter, validate, and save their OpenAI API key
    which is required for transcription services.
    """
    
    def __init__(self, parent=None, current_api_key=""):
        """
        Initialize the APIKeyDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        current_api_key : str, optional
            Current API key, by default ""
        """
        super().__init__(parent)
        
        self.api_key = current_api_key
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle(AppLabels.DIALOG_API_KEY_TITLE)
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create grid for form
        form_layout = QGridLayout()
        
        # Add description
        description = QLabel(
            "Enter your OpenAI API key to use transcription services. "
            "The key will be stored locally on your device."
        )
        description.setWordWrap(True)
        
        # Create API key input
        key_label = QLabel("API Key:")
        self.key_input = QLineEdit(self.api_key)
        self.key_input.setPlaceholderText("Enter your OpenAI API key...")
        
        # Set echo mode to password (hidden text)
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Toggle visibility button
        self.toggle_visibility_button = QPushButton("Show")
        self.toggle_visibility_button.setCheckable(True)
        self.toggle_visibility_button.clicked.connect(self.toggle_key_visibility)
        
        # Add to grid layout
        form_layout.addWidget(description, 0, 0, 1, 3)
        form_layout.addWidget(key_label, 1, 0)
        form_layout.addWidget(self.key_input, 1, 1)
        form_layout.addWidget(self.toggle_visibility_button, 1, 2)
        
        # Add validate button
        validate_button = QPushButton("Validate Key")
        validate_button.clicked.connect(self.validate_api_key)
        
        form_layout.addWidget(validate_button, 2, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        
        # Add button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add layouts to main layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
    
    def toggle_key_visibility(self, checked):
        """
        Toggle the visibility of the API key.
        
        Parameters
        ----------
        checked : bool
            Whether the visibility button is checked.
        """
        if checked:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_visibility_button.setText("Hide")
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_visibility_button.setText("Show")
    
    def validate_api_key(self):
        """
        Validate the entered API key.
        
        This method attempts to create a WhisperTranscriber with the entered key
        to check if it's valid. Shows appropriate message based on the result.
        """
        key = self.key_input.text().strip()
        
        if not key:
            QMessageBox.warning(
                self,
                "Validation Error",
                "API key cannot be empty."
            )
            return
        
        try:
            # Try to create a transcriber with this key
            transcriber = WhisperTranscriber(api_key=key)
            
            # If successful, show confirmation
            QMessageBox.information(
                self,
                "API Key Valid",
                "The API key is valid and has been verified."
            )
        except Exception as e:
            # If failed, show error
            QMessageBox.critical(
                self,
                "Validation Error",
                f"Failed to validate API key: {str(e)}"
            )
    
    def get_api_key(self):
        """
        Get the API key from the input field.
        
        Returns
        -------
        str
            The entered API key.
        """
        return self.key_input.text().strip()
    
    def accept(self):
        """Handle dialog acceptance with validation."""
        # Validate key before accepting
        key = self.get_api_key()
        
        if not key:
            QMessageBox.warning(
                self,
                "Validation Error",
                "API key cannot be empty."
            )
            return
        
        # Update stored key
        self.api_key = key
        
        # Accept the dialog
        super().accept()
