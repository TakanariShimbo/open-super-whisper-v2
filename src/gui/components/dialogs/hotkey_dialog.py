"""
Hotkey Dialog Module

This module provides a dialog for setting a global hotkey for the application.
"""

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QApplication, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.gui.resources.labels import AppLabels
from src.gui.components.dialogs.simple_message_dialog import SimpleMessageDialog


class HotkeyDialog(QDialog):
    """
    Dialog for setting a global hotkey.
    
    This dialog allows users to set or update the global hotkey used
    for starting and stopping recording from anywhere in the system.
    """
    
    # Signals
    hotkey_updated = pyqtSignal(str)
    
    def __init__(self, parent=None, current_hotkey=None):
        """
        Initialize the HotkeyDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget, by default None.
        current_hotkey : str, optional
            The current hotkey to display, by default None.
        """
        super().__init__(parent)
        self.setWindowTitle(AppLabels.HOTKEY_DIALOG_TITLE)
        self.setMinimumWidth(400)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create dialog frame
        dialog_frame = QFrame(self)
        layout = QVBoxLayout(dialog_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Dialog title
        title_label = QLabel(AppLabels.HOTKEY_DIALOG_TITLE)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # Hotkey input
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.hotkey_input = QLineEdit()
        if current_hotkey:
            self.hotkey_input.setText(current_hotkey)
        self.hotkey_input.setPlaceholderText(AppLabels.HOTKEY_PLACEHOLDER)
        
        form_layout.addRow(QLabel(AppLabels.HOTKEY_LABEL), self.hotkey_input)
        
        layout.addLayout(form_layout)
        
        # Information text
        info_label = QLabel(AppLabels.HOTKEY_INFO)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_button = QPushButton(AppLabels.CANCEL_BUTTON)
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton(AppLabels.SAVE_BUTTON)
        self.save_button.clicked.connect(self.accept_with_validation)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        main_layout.addWidget(dialog_frame)
    
    def get_hotkey(self):
        """
        Get the hotkey entered in the dialog.
        
        Returns
        -------
        str
            The hotkey text.
        """
        return self.hotkey_input.text()

    def accept_with_validation(self):
        """
        Validate the hotkey and accept the dialog if valid.
        """
        hotkey = self.hotkey_input.text().strip()
        
        # Check if hotkey is empty
        if not hotkey:
            SimpleMessageDialog.show_message(
                self,
                AppLabels.WARNING_TITLE,
                "Please enter a hotkey.",
                SimpleMessageDialog.WARNING
            )
            return
        
        # Very basic validation - in a real implementation,
        # we would check if the hotkey format is valid
        
        # Emit signal
        self.hotkey_updated.emit(hotkey)
        
        # Accept the dialog
        self.accept()


# For standalone testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show the dialog
    dialog = HotkeyDialog(current_hotkey="ctrl+shift+r")
    result = dialog.exec()
    
    # Show the result
    if result == QDialog.DialogCode.Accepted:
        print(f"Hotkey set: {dialog.hotkey_input.text()}")
    else:
        print("Canceled")
    
    sys.exit()
