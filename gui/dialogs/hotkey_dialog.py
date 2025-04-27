"""
Hotkey Dialog

This module provides a dialog for setting the global hotkey with thread-safe implementation.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QGridLayout
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeyEvent, QKeySequence

from gui.resources.labels import AppLabels
from gui.dialogs.simple_message_dialog import SimpleMessageDialog
from gui.thread_management.hotkey_bridge import HotkeyBridge


class HotkeyDialog(QDialog):
    """
    Dialog for setting the global hotkey.
    
    This dialog allows users to define a custom hotkey combination
    for starting and stopping recording.
    
    Thread Safety:
    --------------
    Uses ThreadManager.run_in_main_thread for showing message dialogs when
    thread_manager is provided. This ensures thread safety for UI operations.
    """
    
    def __init__(self, parent=None, current_hotkey="", thread_manager=None):
        """
        Initialize the HotkeyDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        current_hotkey : str, optional
            Current hotkey string, by default ""
        thread_manager : ThreadManager, optional
            Thread manager for thread-safe operations
        """
        super().__init__(parent)
        
        self.hotkey = current_hotkey
        self.current_keys = set()
        self.thread_manager = thread_manager
        
        # Store original hotkey for safe restoration
        self.original_hotkey = current_hotkey
        
        # Flag to track if hotkeys were disabled
        self.hotkeys_disabled = False
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle(AppLabels.HOTKEY_TITLE)
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create grid for form
        form_layout = QGridLayout()
        
        # Add description
        description = QLabel(AppLabels.HOTKEY_DESCRIPTION)
        description.setWordWrap(True)
        
        # Create hotkey input
        hotkey_label = QLabel(AppLabels.HOTKEY_LABEL)
        self.hotkey_input = QLineEdit(self.hotkey)
        self.hotkey_input.setPlaceholderText(AppLabels.HOTKEY_PLACEHOLDER)
        self.hotkey_input.setReadOnly(True)
        
        # Make the input field receive key events
        self.hotkey_input.installEventFilter(self)
        
        # Reset button
        reset_button = QPushButton(AppLabels.HOTKEY_CLEAR_BUTTON)
        reset_button.clicked.connect(self.reset_hotkey)
        
        # Add to grid layout
        form_layout.addWidget(description, 0, 0, 1, 3)
        form_layout.addWidget(hotkey_label, 1, 0)
        form_layout.addWidget(self.hotkey_input, 1, 1)
        form_layout.addWidget(reset_button, 1, 2)
        
        # Add hotkey examples
        examples_label = QLabel(AppLabels.HOTKEY_EXAMPLES)
        examples_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(examples_label, 2, 0, 1, 3)
        
        # Add button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add layouts to main layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
    
    def eventFilter(self, obj, event):
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
            self.handle_key_press(event)
            return True
        
        return super().eventFilter(obj, event)
    
    def handle_key_press(self, event):
        """
        Handle key press events.
        
        Parameters
        ----------
        event : QKeyEvent
            Key press event.
        """
        # Ignore standalone modifier keys (Ctrl, Alt, Shift)
        key = event.key()
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift, Qt.Key.Key_Meta):
            return
        
        # Get modifier keys
        modifiers = event.modifiers()
        
        # Build hotkey string
        parts = []
        
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("ctrl")
        
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("alt")
        
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("shift")
        
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            parts.append("meta")
        
        # Add the key itself (convert to string)
        key_text = QKeySequence(key).toString().lower()
        
        # Only add if it's not already included in the modifiers
        if key_text not in parts:
            parts.append(key_text)
        
        # Create hotkey string
        hotkey_str = "+".join(parts)
        
        # Update input
        self.hotkey_input.setText(hotkey_str)
        self.hotkey = hotkey_str
    
    def reset_hotkey(self):
        """Reset the hotkey field."""
        self.hotkey_input.clear()
        self.hotkey = ""
    
    def get_hotkey(self):
        """
        Get the hotkey string.
        
        Returns
        -------
        str
            The hotkey combination as a string.
        """
        return self.hotkey
    
    def accept(self):
        """
        Handle dialog acceptance with validation.
        
        This method is called when the OK button is clicked. It validates
        the hotkey and re-enables all hotkeys that were disabled when the
        dialog was shown.
        """
        # Validate hotkey before accepting
        if not self.hotkey:
            self._show_validation_error()
            return
        
        # Re-enable hotkeys
        self._restore_hotkeys()
        
        # Accept the dialog
        super().accept()
    
    def _show_validation_error(self):
        """Show error message for empty hotkey."""
        SimpleMessageDialog.show_message(
            self,
            AppLabels.HOTKEY_VALIDATION_ERROR_TITLE,
            AppLabels.HOTKEY_VALIDATION_ERROR_MESSAGE,
            SimpleMessageDialog.WARNING,
            self.thread_manager
        )
    
    def showEvent(self, event):
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
        
        # Disable all hotkeys by using HotkeyBridge's set_recording_mode
        # Setting enabled=True with an empty recording_hotkey effectively disables all hotkeys
        hotkey_bridge = HotkeyBridge.instance()
        if hotkey_bridge:
            try:
                hotkey_bridge.set_recording_mode(True, None)
                self.hotkeys_disabled = True
            except Exception as e:
                print(f"Error disabling hotkeys: {e}")
    
    def closeEvent(self, event):
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
    
    def reject(self):
        """
        Handle dialog rejection.
        
        This method is called when the Cancel button is clicked. It restores
        the original hotkey and re-enables all hotkeys.
        """
        # Restore original hotkey
        self.hotkey = self.original_hotkey
        
        # Re-enable hotkeys
        self._restore_hotkeys()
        
        # Call parent class method
        super().reject()
    
    def _restore_hotkeys(self):
        """
        Restore hotkeys that were disabled.
        
        This method re-enables all hotkeys that were disabled when the dialog was shown.
        """
        if self.hotkeys_disabled:
            hotkey_bridge = HotkeyBridge.instance()
            if hotkey_bridge:
                try:
                    # Disable recording mode to re-enable all hotkeys
                    hotkey_bridge.set_recording_mode(False)
                    self.hotkeys_disabled = False
                except Exception as e:
                    print(f"Error re-enabling hotkeys: {e}")
