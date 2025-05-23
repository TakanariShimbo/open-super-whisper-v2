"""
Hotkey Dialog Controller

This module provides the controller component for the hotkey dialog,
mediating between the hotkey dialog model and view.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

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

    #
    # Signals
    #
    hotkey_changed = pyqtSignal(str)
    hotkey_captured = pyqtSignal(str)
    validation_error = pyqtSignal(str)  # error_message

    def __init__(self, current_hotkey: str = "", hotkey_dialog: QObject | None = None) -> None:
        """
        Initialize the HotkeyDialogController.

        Parameters
        ----------
        current_hotkey : str, optional
            Initial hotkey value, by default ""
        hotkey_dialog : QObject | None, optional
            Parent object for this controller, by default None
        """
        super().__init__(parent=hotkey_dialog)

        # Create model
        self._model = HotkeyDialogModel(current_hotkey=current_hotkey, hotkey_dialog=hotkey_dialog)

        # Connect model signals
        self._connect_model_signals()

    #
    # Model Signals
    #
    def _connect_model_signals(self) -> None:
        """
        Connect signals from the model to controller handlers.
        """
        self._model.hotkey_changed.connect(self._handle_hotkey_changed)
        self._model.hotkey_captured.connect(self._handle_hotkey_captured)
        self._model.validation_failed.connect(self._handle_validation_failed)

    #
    # Model Events
    #
    @pyqtSlot(str)
    def _handle_hotkey_changed(self, hotkey: str) -> None:
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
    def _handle_hotkey_captured(self, hotkey: str) -> None:
        """
        Handle hotkey captured event from the model.

        Parameters
        ----------
        hotkey : str
            The captured hotkey
        """
        # Forward signal to view
        self.hotkey_captured.emit(hotkey)

    @pyqtSlot(str)
    def _handle_validation_failed(self, error_message: str) -> None:
        """
        Handle failed validation from the model.

        Parameters
        ----------
        error_message : str
            Error message from validation
        """
        # Forward error message to view
        self.validation_error.emit(error_message)

    #
    # Controller Methods
    #
    def get_hotkey(self) -> str:
        """
        Get the current hotkey.

        Returns
        -------
        str
            The current hotkey string
        """
        return self._model.get_hotkey()

    def start_capturing(self) -> None:
        """
        Start capturing keyboard input.
        """
        self._model.start_capturing()

    def stop_capturing(self) -> None:
        """
        Stop capturing keyboard input.
        """
        self._model.stop_capturing()

    def capture_keys(self) -> None:
        """
        Capture the key combination.
        """
        self._model.capture_keys()

    def set_hotkey(self, hotkey: str) -> None:
        """
        Set the hotkey directly.

        Parameters
        ----------
        hotkey : str
            The hotkey string to set
        """
        self._model.set_hotkey(value=hotkey)

    def reset_hotkey(self) -> None:
        """
        Reset the hotkey to empty.
        """
        self._model.reset()

    def validate_hotkey(self) -> bool:
        """
        Validate the current hotkey.

        Returns
        -------
        bool
            True if the hotkey is valid, False otherwise
        """
        return self._model.validate_hotkey()

    def save(self) -> None:
        """
        Save the current hotkey as the new original.
        """
        self._model.save()

    def cancel(self) -> None:
        """
        Cancel the dialog and restore the original hotkey.
        """
        # Stop any active capturing
        self.stop_capturing()

        # Restore original value
        self._model.restore_original()
