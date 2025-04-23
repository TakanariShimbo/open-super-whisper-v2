"""
OpenAI API Key Dialog Module

This module provides a dialog for entering and managing the OpenAI API key.
"""

import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QMessageBox, QApplication, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.gui.resources.labels import AppLabels
from src.gui.components.dialogs.simple_message_dialog import SimpleMessageDialog


class APIKeyDialog(QDialog):
    """
    Dialog for entering and managing the OpenAI API key.
    
    This dialog allows users to enter or update their OpenAI API key,
    which is required for using the Whisper transcription service.
    """
    
    # Signals
    api_key_updated = pyqtSignal(str)
    
    def __init__(self, parent=None, api_key=None):
        """
        Initialize the APIKeyDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            The parent widget, by default None.
        api_key : str, optional
            The current API key to display, by default None.
        """
        super().__init__(parent)
        self.setWindowTitle(AppLabels.API_KEY_DIALOG_TITLE)
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
        title_label = QLabel(AppLabels.API_KEY_DIALOG_TITLE)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # API key input
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.api_key_input = QLineEdit()
        if api_key:
            self.api_key_input.setText(api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow(QLabel(AppLabels.API_KEY_LABEL), self.api_key_input)
        
        layout.addLayout(form_layout)
        
        # Information text
        info_label = QLabel(AppLabels.API_KEY_INFO)
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
    
    def get_api_key(self):
        """
        Get the API key entered in the dialog.
        
        Returns
        -------
        str
            The API key text.
        """
        return self.api_key_input.text()

    def accept_with_validation(self):
        """
        Validate the API key and accept the dialog if valid.
        """
        api_key = self.api_key_input.text().strip()
        
        # Check if API key is empty
        if not api_key:
            SimpleMessageDialog.show_message(
                self,
                AppLabels.WARNING_TITLE,
                AppLabels.APIKEY_EMPTY_WARNING,
                SimpleMessageDialog.WARNING
            )
            return
        
        # Check if API key is too short
        if len(api_key) < 10:
            SimpleMessageDialog.show_message(
                self,
                AppLabels.WARNING_TITLE,
                AppLabels.APIKEY_TOO_SHORT_WARNING,
                SimpleMessageDialog.WARNING
            )
            return
        
        # Emit signal
        self.api_key_updated.emit(api_key)
        
        # Accept the dialog
        self.accept()


# For standalone testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show the dialog
    dialog = APIKeyDialog()
    result = dialog.exec()
    
    # Show the result
    if result == QDialog.DialogCode.Accepted:
        print(f"API key set: {dialog.api_key_input.text()}")
    else:
        print("Canceled")
    
    sys.exit()
