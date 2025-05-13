"""
Hotkey Dialog Controller

This module provides the controller component for the hotkey dialog,
mediating between the hotkey dialog model and view.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QKeyEvent

from ...models.dialogs.hotkey_dialog_model import HotkeyDialogModel


class HotkeyDialogController(QObject):
    """
    Controller for the hotkey dialog.
    
    This class coordinates between the hotkey dialog model and view,
    handling user interactions, key events, and validation logic.
    
    Attributes
    ----------
    hotkey_changed : pyqtSignal
        Signal emitted when the hotkey changes
    hotkey_captured : pyqtSignal
        Signal emitted when a key combination is captured
    validation_error : pyqtSignal
        Signal emitted when validation fails
    """
    
    # Define signals for view communication
    hotkey_changed = pyqtSignal(str)
    hotkey_captured = pyqtSignal(str)
    validation_error = pyqtSignal(str)  # error_message
    
    def __init__(self, current_hotkey: str = "", 
                 conflict_checker=None, 
                 parent_controller: QObject | None = None) -> None:
        """
        Initialize the HotkeyDialogController.
        
        Parameters
        ----------
        current_hotkey : str, optional
            Initial hotkey value, by default ""
        conflict_checker : callable, optional
            Function that checks for hotkey conflicts, by default None
            Should take a hotkey string and return None or an error message
        parent_controller : QObject | None, optional
            Parent controller for this controller, by default None
        """
        super().__init__()
        
        # Create model
        self._dialog_model = HotkeyDialogModel(current_hotkey)
        self._parent_controller = parent_controller
        self._conflict_checker = conflict_checker
        
        # Connect model signals
        self._connect_model_signals()
    
    def _connect_model_signals(self) -> None:
        """
        Connect signals from the model to controller handlers.
        """
        self._dialog_model.hotkey_changed.connect(self._on_hotkey_changed)
        self._dialog_model.hotkey_captured.connect(self._on_hotkey_captured)
        self._dialog_model.validation_succeeded.connect(self._on_validation_succeeded)
        self._dialog_model.validation_failed.connect(self._on_validation_failed)
    
    @pyqtSlot(str)
    def _on_hotkey_changed(self, hotkey: str) -> None:
        """
        Handle hotkey changed event from the model.
        
        Parameters
        ----------
        hotkey : str
            The new hotkey value
        """
        # Forward signal to view
        self.hotkey_changed.emit(hotkey)
    
    @pyqtSlot(str)
    def _on_hotkey_captured(self, hotkey: str) -> None:
        """
        Handle hotkey captured event from the model.
        
        Parameters
        ----------
        hotkey : str
            The captured hotkey
        """
        # Forward signal to view
        self.hotkey_captured.emit(hotkey)
    
    @pyqtSlot()
    def _on_validation_succeeded(self) -> None:
        """
        Handle successful validation from the model.
        """
        # Nothing to do, just let the dialog proceed
        pass
    
    @pyqtSlot(str)
    def _on_validation_failed(self, error_message: str) -> None:
        """
        Handle failed validation from the model.
        
        Parameters
        ----------
        error_message : str
            Error message from validation
        """
        # Forward error message to view
        self.validation_error.emit(error_message)
    
    def get_hotkey(self) -> str:
        """
        Get the current hotkey.
        
        Returns
        -------
        str
            The current hotkey string
        """
        return self._dialog_model.hotkey
    
    def start_capturing(self) -> None:
        """
        Start capturing keyboard input.
        """
        self._dialog_model.start_capturing()
    
    def stop_capturing(self) -> None:
        """
        Stop capturing keyboard input.
        """
        self._dialog_model.stop_capturing()
    
    def capture_keys(self) -> None:
        """
        Capture the current key combination.
        """
        self._dialog_model.capture_current_keys()
    
    def set_hotkey(self, hotkey: str) -> None:
        """
        Set the hotkey directly.
        
        Parameters
        ----------
        hotkey : str
            The hotkey string to set
        """
        self._dialog_model.hotkey = hotkey
    
    def reset_hotkey(self) -> None:
        """
        Reset the hotkey to empty.
        """
        self._dialog_model.reset()
    
    def validate_and_accept(self) -> bool:
        """
        Validate the current hotkey.
        
        Returns
        -------
        bool
            True if the hotkey is valid, False otherwise
        """
        return self._dialog_model.validate_hotkey(self._conflict_checker)
    
    def save(self) -> None:
        """
        Save the current hotkey as the new original.
        """
        self._dialog_model.save()
    
    def cancel(self) -> None:
        """
        Cancel the dialog and restore the original hotkey.
        """
        # Stop any active capturing
        self.stop_capturing()
        
        # Restore original value
        self._dialog_model.restore_original()
