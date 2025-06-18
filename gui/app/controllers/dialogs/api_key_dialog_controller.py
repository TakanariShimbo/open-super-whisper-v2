"""
API Key Controller

This module provides the controller component for API key management.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from ...models.dialogs.api_key_dialog_model import APIKeyDialogModel
from ...managers.keyboard_manager import KeyboardManager


class APIKeyDialogController(QObject):
    """
    Controller for API key dialog.

    This class coordinates between the API key dialog model and view components,
    handling user interactions and business logic.

    Signals
    -------
    api_key_validated : pyqtSignal
        Signal emitted when an API key is validated successfully
    api_key_invalid : pyqtSignal
        Signal emitted when an API key validation fails
    """

    #
    # Signals
    #
    api_key_validated = pyqtSignal()
    api_key_invalid = pyqtSignal(str)
    single_api_key_verified = pyqtSignal(str)
    single_api_key_verification_failed = pyqtSignal(str)

    def __init__(self, api_key_dialog: QObject | None = None) -> None:
        """
        Initialize the API Key Controller.

        Parameters
        ----------
        api_key_dialog : QObject | None, optional
            The parent object, by default None
        """
        super().__init__(parent=api_key_dialog)

        # Initialize the model
        self._model = APIKeyDialogModel(api_key_dialog=api_key_dialog)
        
        # Get keyboard manager for hotkey control
        self._keyboard_manager = KeyboardManager.get_instance()

    #
    # Controller Methods
    #
    def validate_api_key(self, openai_api_key: str, anthropic_api_key: str, gemini_api_key: str) -> bool:
        """
        Validate the given OpenAI API key.

        Parameters
        ----------
        openai_api_key : str
            The OpenAI API key to validate

        Returns
        -------
        bool
            True if the API key is valid, False otherwise
        """
        # Validate the API key
        if not self._model.validate_openai_api_key(openai_api_key=openai_api_key):
            self.api_key_invalid.emit("OpenAI")
            return False
        
        if anthropic_api_key:
            if not self._model.validate_anthropic_api_key(anthropic_api_key=anthropic_api_key):
                self.api_key_invalid.emit("Anthropic")
                return False

        if gemini_api_key:
            if not self._model.validate_gemini_api_key(gemini_api_key=gemini_api_key):
                self.api_key_invalid.emit("Gemini")
                return False
        
        # Set the valid key in the model
        self._model.set_openai_api_key(openai_api_key=openai_api_key)
        self._model.set_anthropic_api_key(anthropic_api_key=anthropic_api_key)
        self._model.set_gemini_api_key(gemini_api_key=gemini_api_key)

        # Emit signal for validation success
        self.api_key_validated.emit()

        return True

    def get_openai_api_key(self) -> str:
        """
        Get current OpenAI API key.

        Returns
        -------
        str
            The current API key
        """
        return self._model.get_openai_api_key()

    def get_anthropic_api_key(self) -> str:
        """
        Get current Anthropic API key.

        Returns
        -------
        str
            The current API key
        """
        return self._model.get_anthropic_api_key()

    def get_gemini_api_key(self) -> str:
        """
        Get current Gemini API key.

        Returns
        -------
        str
            The current API key
        """
        return self._model.get_gemini_api_key()

    def save_api_key(self) -> None:
        """
        Save current API key to persistent storage.
        """
        self._model.save_api_key()
    
    def verify_single_api_key(self, provider: str, api_key: str) -> None:
        """
        Verify a single API key asynchronously.
        
        Parameters
        ----------
        provider : str
            The API provider (openai, anthropic, or gemini)
        api_key : str
            The API key to verify
        """
        # Run verification in a separate thread to avoid blocking UI
        from PyQt6.QtCore import QThread
        
        class VerificationThread(QThread):
            def __init__(self, model, provider, api_key):
                super().__init__()
                self.model = model
                self.provider = provider
                self.api_key = api_key
                self.result = False
            
            def run(self):
                if self.provider == "openai":
                    self.result = self.model.validate_openai_api_key(self.api_key)
                elif self.provider == "anthropic":
                    self.result = self.model.validate_anthropic_api_key(self.api_key)
                elif self.provider == "gemini":
                    self.result = self.model.validate_gemini_api_key(self.api_key)
        
        thread = VerificationThread(self._model, provider, api_key)
        thread.finished.connect(lambda: self._handle_verification_result(provider, thread.result))
        thread.finished.connect(thread.deleteLater)
        thread.start()
    
    def _handle_verification_result(self, provider: str, is_valid: bool) -> None:
        """
        Handle the verification result.
        
        Parameters
        ----------
        provider : str
            The API provider
        is_valid : bool
            Whether the API key is valid
        """
        if is_valid:
            self.single_api_key_verified.emit(provider)
        else:
            self.single_api_key_verification_failed.emit(provider)

    def cancel(self) -> None:
        """
        Cancel dialog and restore original API key.
        """
        self._model.restore_original()

    def start_listening(self) -> bool:
        """
        Start listening for hotkeys.

        Returns
        -------
        bool
            True if listening started successfully, False otherwise
        """
        return self._keyboard_manager.start_listening()

    def stop_listening(self) -> bool:
        """
        Stop listening for hotkeys.

        Returns
        -------
        bool
            True if listening stopped successfully, False otherwise
        """
        return self._keyboard_manager.stop_listening()
