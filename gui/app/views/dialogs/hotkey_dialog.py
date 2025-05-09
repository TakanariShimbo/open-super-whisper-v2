"""
Hotkey Dialog View

This module provides the view component for setting hotkeys in the Super Whisper application.
It integrates the MVC components of the hotkey dialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QEvent, pyqtSlot, QObject
from PyQt6.QtGui import QCloseEvent, QShowEvent

from ...controllers.dialogs.hotkey_dialog_controller import HotkeyDialogController


class HotkeyDialog(QDialog):
    """
    Dialog for setting global hotkeys.
    
    This dialog allows users to define a custom hotkey combination
    for various actions in the application.
    """
    
    def __init__(self, parent=None, current_hotkey="", hotkey_manager=None) -> None:
        """
        Initialize the HotkeyDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        current_hotkey : str, optional
            Current hotkey string, by default ""
        hotkey_manager : object, optional
            An object that can manage hotkeys, should have enable_hotkeys() and disable_hotkeys() methods
        """
        super().__init__(parent)
        
        # Create controller
        self._controller = HotkeyDialogController(current_hotkey)
        
        # Store hotkey manager
        self._hotkey_manager = hotkey_manager
        
        # Flag to track if hotkeys were disabled
        self._hotkeys_disabled = False
        
        # Set up UI
        self._init_ui()
        
        # Connect controller signals
        self._connect_controller_signals()
    
    def _init_ui(self) -> None:
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle("Hotkey Settings")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create grid for form
        form_layout = QGridLayout()
        
        # Add description
        description = QLabel("Set a global hotkey combination for this action.")
        description.setWordWrap(True)
        
        # Create hotkey input
        hotkey_label = QLabel("Hotkey:")
        self.hotkey_input = QLineEdit(self._controller.get_hotkey())
        self.hotkey_input.setPlaceholderText("Press keys to set hotkey")
        self.hotkey_input.setReadOnly(True)
        
        # Make the input field receive key events
        self.hotkey_input.installEventFilter(self)
        
        # Reset button
        reset_button = QPushButton("Clear")
        reset_button.clicked.connect(self._on_reset_clicked)
        
        # Add to grid layout
        form_layout.addWidget(description, 0, 0, 1, 3)
        form_layout.addWidget(hotkey_label, 1, 0)
        form_layout.addWidget(self.hotkey_input, 1, 1)
        form_layout.addWidget(reset_button, 1, 2)
        
        # Add hotkey examples
        examples_label = QLabel("Examples: ctrl+shift+r, alt+a, ctrl+alt+s")
        examples_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(examples_label, 2, 0, 1, 3)
        
        # Add button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self._on_reject)
        
        # Add layouts to main layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
    
    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller.
        """
        self._controller.hotkey_changed.connect(self._on_hotkey_changed)
        self._controller.validation_error.connect(self._show_validation_error)
    
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Event filter to capture key presses.
        
        Parameters
        ----------
        obj : QObject
            Object that received the event.
        event : QEvent
            Event that was received.
            
        Returns
        -------
        bool
            Whether the event was handled.
        """
        if obj == self.hotkey_input and event.type() == QEvent.Type.KeyPress:
            # Handle key press through controller
            self._controller.handle_key_press(event)
            return True
        
        return super().eventFilter(obj, event)
    
    @pyqtSlot()
    def _on_reset_clicked(self) -> None:
        """
        Handle reset button click.
        """
        self._controller.reset_hotkey()
    
    @pyqtSlot(str)
    def _on_hotkey_changed(self, hotkey: str) -> None:
        """
        Handle hotkey changed event from the controller.
        
        Parameters
        ----------
        hotkey : str
            The new hotkey value
        """
        self.hotkey_input.setText(hotkey)
    
    @pyqtSlot(str, str)
    def _show_validation_error(self, title: str, message: str) -> None:
        """
        Display a validation error message.
        
        Parameters
        ----------
        title : str
            Error dialog title
        message : str
            Error message
        """
        QMessageBox.warning(self, title, message)
    
    def _on_accept(self) -> None:
        """
        Handle dialog acceptance.
        
        This method is called when the OK button is clicked. It validates
        the hotkey and re-enables all hotkeys that were disabled.
        """
        # Validate hotkey before accepting
        if not self._controller.validate_and_accept():
            return
        
        # Re-enable hotkeys
        self._restore_hotkeys()
        
        # Accept the dialog
        super().accept()
    
    def _on_reject(self) -> None:
        """
        Handle dialog rejection.
        
        This method is called when the Cancel button is clicked. It restores
        the original hotkey and re-enables all hotkeys.
        """
        # Tell controller to restore original hotkey
        self._controller.cancel()
        
        # Re-enable hotkeys
        self._restore_hotkeys()
        
        # Reject the dialog
        super().reject()
    
    def get_hotkey(self) -> str:
        """
        Get the hotkey string.
        
        Returns
        -------
        str
            The hotkey combination as a string.
        """
        return self._controller.get_hotkey()
    
    def showEvent(self, event: QShowEvent) -> None:
        """
        Handle dialog show event.
        
        This method is called when the dialog is shown. It disables all hotkeys
        to prevent them from being triggered while the dialog is open.
        
        Parameters
        ----------
        event : QShowEvent
            Show event
        """
        # Call parent class method first
        super().showEvent(event)
        
        # Disable hotkeys if a hotkey manager is provided
        if self._hotkey_manager and hasattr(self._hotkey_manager, 'disable_hotkeys'):
            try:
                self._hotkey_manager.disable_hotkeys()
                self._hotkeys_disabled = True
            except Exception as e:
                print(f"Error disabling hotkeys: {e}")
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle dialog close event.
        
        This method is called when the dialog is closed. It re-enables all hotkeys
        that were disabled when the dialog was shown.
        
        Parameters
        ----------
        event : QCloseEvent
            Close event
        """
        # Re-enable hotkeys
        self._restore_hotkeys()
        
        # Call parent class method
        super().closeEvent(event)
    
    def _restore_hotkeys(self) -> None:
        """
        Restore hotkeys that were disabled.
        
        This method re-enables all hotkeys that were disabled when the dialog was shown.
        """
        if self._hotkeys_disabled and self._hotkey_manager and hasattr(self._hotkey_manager, 'enable_hotkeys'):
            try:
                self._hotkey_manager.enable_hotkeys()
                self._hotkeys_disabled = False
            except Exception as e:
                print(f"Error re-enabling hotkeys: {e}")
