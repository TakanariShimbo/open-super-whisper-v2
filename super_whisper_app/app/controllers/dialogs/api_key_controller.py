"""
API Key Controller

This module provides the controller component for API key management.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMessageBox

from ...models.dialogs.api_key_model import APIKeyModel
from ...views.dialogs.api_key_dialog import APIKeyDialog

class APIKeyController(QObject):
    """
    Controller for API key management.
    
    This class coordinates between the API key model and view components,
    handling user interactions and business logic.
    
    Signals
    -------
    api_key_validated : pyqtSignal
        Signal emitted when an API key is validated successfully
    api_key_invalid : pyqtSignal
        Signal emitted when an API key validation fails
    """
    
    # Define signals
    api_key_validated = pyqtSignal(str)
    api_key_invalid = pyqtSignal(str)
    
    def __init__(self, settings):
        """
        Initialize the API Key Controller.
        
        Parameters
        ----------
        settings : QSettings
            Application settings for persistent storage
        """
        super().__init__()
        
        # Initialize the model
        self._api_key_model = APIKeyModel(settings)
    
    def ensure_valid_api_key(self, parent=None):
        """
        Ensure a valid API key is available, prompting the user if necessary.
        
        This method checks for a valid API key and prompts the user to enter one
        if no valid key is found.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for dialogs, by default None
            
        Returns
        -------
        bool
            True if a valid API key is available, False otherwise
        """
        # Check if we already have a valid API key
        api_key = self._api_key_model.get_api_key()
        initial_message = None
        
        # Validate existing API key if available
        if api_key:
            if self._api_key_model.validate_api_key(api_key):
                # API key is valid
                self.api_key_validated.emit(api_key)
                return True
            else:
                # API key is invalid, show warning and clear it
                QMessageBox.warning(
                    parent,
                    "API Key Error",
                    "The saved API key is no longer valid. You will need to enter a new API key."
                )
                initial_message = "Previous API key is invalid. Please enter a new one."
                self._api_key_model.clear_api_key()
        else:
            # No API key set, show welcome message
            initial_message = "Welcome to Super Whisper! Please enter your OpenAI API key to get started."
        
        # Prompt for API key
        return self.prompt_for_api_key(parent, initial_message)
    
    def prompt_for_api_key(self, parent=None, initial_message=None, is_settings_mode=False):
        """
        Prompt the user to enter an API key.
        
        This method creates and displays an API key dialog, and handles the
        validation and storage of the entered key.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
        initial_message : str, optional
            Initial message to display in the dialog, by default None
        is_settings_mode : bool, optional
            Whether the dialog is being used in settings mode, by default False
            
        Returns
        -------
        bool
            True if a valid API key was entered, False if the user cancelled
        """
        # Get current API key to pre-fill in settings mode
        current_api_key = ""
        if is_settings_mode:
            current_api_key = self._api_key_model.get_api_key()
            
        while True:
            # Create dialog
            dialog = APIKeyDialog(parent, initial_message, is_settings_mode)
            
            # Set current API key if in settings mode
            if current_api_key:
                dialog._api_key_input.setText(current_api_key)
                
            # Connect dialog signals
            dialog.api_key_entered.connect(self._on_api_key_entered)
            
            # Track if we've validated a key
            self._validation_successful = False
            self._current_dialog = dialog
            
            # Show dialog
            result = dialog.exec()
            
            # Check result
            if result == 0:  # QDialog.Rejected (user cancelled)
                return False
            
            # If validation was successful, we can exit the loop
            if self._validation_successful:
                return True
            
            # If we reach here, validation failed but the dialog was accepted
            # Set error message for next iteration
            initial_message = "Invalid API key. Please try again."
    
    @pyqtSlot(str)
    def _on_api_key_entered(self, api_key):
        """
        Handle API key entered by the user.
        
        This method validates the entered API key and updates the model
        if the key is valid.
        
        Parameters
        ----------
        api_key : str
            The API key entered by the user
        """
        # Validate the API key
        if self._api_key_model.validate_api_key(api_key):
            # Save the valid API key
            self._api_key_model.set_api_key(api_key)
            
            # Emit signal
            self.api_key_validated.emit(api_key)
            
            # Update status and close dialog
            self._validation_successful = True
            self._current_dialog.accept()
        else:
            # Show error message
            self._current_dialog.show_message("Invalid API key. Please check and try again.")
            
            # Emit signal
            self.api_key_invalid.emit(api_key)
