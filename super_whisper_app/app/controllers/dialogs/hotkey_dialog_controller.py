"""
Hotkey Dialog Controller

This module provides the controller component for the hotkey dialog,
mediating between the model and view.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QKeyEvent

from ...models.dialogs.hotkey_dialog_model import HotkeyDialogModel


class HotkeyDialogController(QObject):
    """
    Controller for the hotkey dialog.
    
    This class mediates between the hotkey dialog view and model,
    handling user interactions and updating the model and view accordingly.
    
    Attributes
    ----------
    hotkey_changed : pyqtSignal
        Signal emitted when the hotkey is changed
    validation_error : pyqtSignal
        Signal emitted when there's a validation error
    """
    
    # Define signals for view communication
    hotkey_changed = pyqtSignal(str)
    validation_error = pyqtSignal(str, str)  # title, message
    
    def __init__(self, 
                 current_hotkey: str = "",
                 parent_controller: QObject | None = None) -> None:
        """
        Initialize the HotkeyDialogController.
        
        Parameters
        ----------
        current_hotkey : str, optional
            Current hotkey string, by default ""
        parent_controller : QObject | None, optional
            The parent controller, by default None
        """
        super().__init__()
        
        # Create model
        self._dialog_model = HotkeyDialogModel(current_hotkey)
        self._parent_controller = parent_controller
        
        # Connect model signals
        self._connect_model_signals()
    
    def _connect_model_signals(self) -> None:
        """
        Connect signals from the model.
        """
        self._dialog_model.hotkey_changed.connect(self._on_hotkey_changed)
        self._dialog_model.hotkey_invalid.connect(self._on_hotkey_invalid)
    
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
    
    @pyqtSlot(str, str)
    def _on_hotkey_invalid(self, hotkey: str, message: str) -> None:
        """
        Handle hotkey validation error from the model.
        
        Parameters
        ----------
        hotkey : str
            The invalid hotkey
        message : str
            Error message
        """
        # Forward validation error to view
        self.validation_error.emit("Hotkey Validation Error", message)
    
    def get_hotkey(self) -> str:
        """
        Get the current hotkey.
        
        Returns
        -------
        str
            The current hotkey string
        """
        return self._dialog_model.hotkey
    
    def handle_key_press(self, event: QKeyEvent) -> None:
        """
        Process a key press event from the view.
        
        Parameters
        ----------
        event : QKeyEvent
            The key press event to process
        """
        from PyQt6.QtCore import Qt
        
        # Ignore standalone modifier keys
        key = event.key()
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift, Qt.Key.Key_Meta):
            return
        
        # Create hotkey string from key and modifiers
        modifiers = event.modifiers()
        hotkey_str = self._dialog_model.create_hotkey_string(key, modifiers)
        
        # Update model with new hotkey
        self._dialog_model.hotkey = hotkey_str
    
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
        return self._dialog_model.validate_hotkey()
    
    def cancel(self) -> None:
        """
        Cancel the dialog and restore the original hotkey.
        """
        self._dialog_model.restore_original()
