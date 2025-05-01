"""
API Key Dialog

This module provides a dialog for setting and validating the OpenAI API key
with thread-safe implementation.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSlot

from old_core.transcriber import OpenAIWhisperTranscriber
from gui.resources.labels import AppLabels
from gui.dialogs.simple_message_dialog import SimpleMessageDialog


class APIKeyDialog(QDialog):
    """
    Dialog for managing the OpenAI API key.
    
    This dialog allows users to enter, validate, and save their OpenAI API key
    which is required for transcription services.
    
    Thread Safety:
    --------------
    API key validation is performed using ThreadManager.run_in_worker_thread when 
    thread_manager is provided. UI updates use ThreadManager.run_in_main_thread
    to ensure thread safety.
    """
    
    def __init__(self, parent=None, current_api_key="", thread_manager=None):
        """
        Initialize the APIKeyDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        current_api_key : str, optional
            Current API key, by default ""
        thread_manager : ThreadManager, optional
            Thread manager for thread-safe operations
        """
        super().__init__(parent)
        
        self.api_key = current_api_key
        self.thread_manager = thread_manager
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle(AppLabels.API_KEY_TITLE)
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create grid for form
        form_layout = QGridLayout()
        
        # Add description
        description = QLabel(AppLabels.API_KEY_DESCRIPTION)
        description.setWordWrap(True)
        
        # Create API key input
        key_label = QLabel(AppLabels.API_KEY_LABEL)
        self.key_input = QLineEdit(self.api_key)
        self.key_input.setPlaceholderText(AppLabels.API_KEY_PLACEHOLDER)
        
        # Set echo mode to password (hidden text)
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Toggle visibility button
        self.toggle_visibility_button = QPushButton(AppLabels.API_KEY_SHOW_BUTTON)
        self.toggle_visibility_button.setCheckable(True)
        self.toggle_visibility_button.clicked.connect(self.toggle_key_visibility)
        
        # Add to grid layout
        form_layout.addWidget(description, 0, 0, 1, 3)
        form_layout.addWidget(key_label, 1, 0)
        form_layout.addWidget(self.key_input, 1, 1)
        form_layout.addWidget(self.toggle_visibility_button, 1, 2)
        
        # Add validate button
        validate_button = QPushButton(AppLabels.API_KEY_VALIDATE_BUTTON)
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
            self.toggle_visibility_button.setText(AppLabels.API_KEY_HIDE_BUTTON)
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_visibility_button.setText(AppLabels.API_KEY_SHOW_BUTTON)
    
    def validate_api_key(self):
        """
        Validate the entered API key.
        
        This method attempts to create a WhisperTranscriber with the entered key
        to check if it's valid. Shows appropriate message based on the result.
        Uses ThreadManager for thread-safe operation if available.
        """
        key = self.key_input.text().strip()
        
        if not key:
            self._show_empty_key_error()
            return
            
        # Define the validation worker function
        def validation_worker():
            try:
                # Try to create a transcriber with this key
                transcriber = OpenAIWhisperTranscriber(api_key=key)
                return True, None
            except Exception as e:
                return False, str(e)
                
        # Define the completion handler
        def on_validation_complete(result):
            success, error = result
            
            if success:
                self._show_key_valid_message()
            else:
                self._show_key_validation_error(error)
                
        # Use thread manager if available, otherwise validate synchronously
        if self.thread_manager:
            self.thread_manager.run_in_worker_thread(
                "api_key_validation",
                validation_worker,
                callback=on_validation_complete
            )
        else:
            # Synchronous validation
            result = validation_worker()
            on_validation_complete(result)
    
    def _show_empty_key_error(self):
        """Show error message for empty API key."""
        SimpleMessageDialog.show_message(
            self,
            AppLabels.API_KEY_EMPTY_ERROR_TITLE,
            AppLabels.API_KEY_EMPTY_ERROR_MESSAGE,
            SimpleMessageDialog.WARNING,
            self.thread_manager
        )
    
    def _show_key_valid_message(self):
        """Show confirmation message for valid API key."""
        SimpleMessageDialog.show_message(
            self,
            AppLabels.API_KEY_VALID_TITLE,
            AppLabels.API_KEY_VALID_MESSAGE,
            SimpleMessageDialog.INFO,
            self.thread_manager
        )
    
    def _show_key_validation_error(self, error_message):
        """
        Show error message for API key validation failure.
        
        Parameters
        ----------
        error_message : str
            Error message to display
        """
        SimpleMessageDialog.show_message(
            self,
            AppLabels.API_KEY_VALIDATION_ERROR_TITLE,
            AppLabels.API_KEY_VALIDATION_ERROR_MESSAGE.format(error_message),
            SimpleMessageDialog.ERROR,
            self.thread_manager
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
            self._show_empty_key_error()
            return
        
        # Update stored key
        self.api_key = key
        
        # Accept the dialog
        super().accept()
