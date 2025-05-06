"""
Main Window Module

This module implements the main window component of the MVC architecture.
It defines the user interface elements and connects UI events to the
appropriate controller methods.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QStatusBar, QHBoxLayout, 
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QFont, QKeySequence, QShortcut

from ..controllers.recorder_controller import RecorderController

class MainWindow(QMainWindow):
    """
    Main application window with UI elements.
    
    This class represents the main window of the application. It contains
    the UI components and connects to the application controller to handle
    user interactions.
    
    Attributes
    ----------
    controller : RecorderController
        The application controller that manages the business logic
    record_button : QPushButton
        Button to start/stop recording
    status_label : QLabel
        Label showing the current status of the application
    hotkey_info_label : QLabel
        Label showing information about hotkeys
    """
    
    def __init__(self) -> None:
        """
        Initialize the MainWindow.
        
        Sets up the user interface and connects signals from the controller
        to UI slots.
        """
        super().__init__()
        
        # Initialize UI
        self.setup_user_interface()
        
        # Initialize controller (business logic)
        self.controller = RecorderController()
        
        # Connect signals from controller to UI slots
        self.controller.recording_state_changed.connect(self.update_recording_state)
        self.controller.recording_file_saved.connect(self.handle_file_saved)
        self.controller.error_occurred.connect(self.display_error)
        self.controller.status_message.connect(self.update_status_message)
        
        # Start listening for hotkeys
        self.controller.start_listening_for_hotkeys()
        
    def setup_user_interface(self) -> None:
        """
        Setup and initialize the user interface components.
        
        Creates and configures all UI components including the window layout,
        title, buttons, status label, and hotkey information.
        """
        # Set window properties
        self.setWindowTitle("Simple Audio Recorder")
        self.setMinimumSize(400, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add title label
        title_label = QLabel("Audio Recorder")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Add recording button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                min-height: 50px;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.record_button.clicked.connect(self.toggle_recording)
        main_layout.addWidget(self.record_button)
        
        # Add status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; margin: 10px;")
        main_layout.addWidget(self.status_label)
        
        # Add hotkey information
        self.hotkey_info_label = QLabel("Press Ctrl+Shift+R to toggle recording")
        self.hotkey_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hotkey_info_label.setStyleSheet("font-style: italic; margin: 5px;")
        main_layout.addWidget(self.hotkey_info_label)
        
        # Add spacer
        main_layout.addStretch(1)
        
        # Add status bar
        self.statusBar().showMessage("Application ready")
    
    @pyqtSlot()
    def toggle_recording(self) -> None:
        """
        Handle when the record button is clicked by the user.
        
        Delegates to the controller to toggle recording state.
        """
        self.controller.toggle_recording()
    
    @pyqtSlot(bool)
    def update_recording_state(self, is_recording: bool) -> None:
        """
        Update the UI to reflect the current recording state.
        
        Parameters
        ----------
        is_recording : bool
            True if recording is in progress, False otherwise
        """
        if is_recording:
            self.record_button.setText("Stop Recording")
            self.record_button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    min-height: 50px;
                    padding: 10px;
                    background-color: #f44336;
                    color: white;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            self.statusBar().showMessage("Recording in progress...")
        else:
            self.record_button.setText("Start Recording")
            self.record_button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    min-height: 50px;
                    padding: 10px;
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.statusBar().showMessage("Recording stopped")
    
    @pyqtSlot(str)
    def handle_file_saved(self, file_path: str) -> None:
        """
        Handle when a recording file is saved.
        
        Parameters
        ----------
        file_path : str
            Path to the saved recording file
        """
        self.status_label.setText(f"File saved: {file_path}")
        
        # Show a message box with the file path
        QMessageBox.information(
            self,
            "Recording Saved",
            f"Recording saved to:\n{file_path}",
            QMessageBox.StandardButton.Ok
        )
    
    @pyqtSlot(str)
    def display_error(self, error_message: str) -> None:
        """
        Display an error message.
        
        Parameters
        ----------
        error_message : str
            Error message to display
        """
        self.status_label.setText(f"Error: {error_message}")
        self.statusBar().showMessage(f"Error: {error_message}")
        
        # Show error message in a message box
        QMessageBox.critical(
            self,
            "Error",
            error_message,
            QMessageBox.StandardButton.Ok
        )
    
    @pyqtSlot(str)
    def update_status_message(self, message: str) -> None:
        """
        Update the status message.
        
        Parameters
        ----------
        message : str
            Status message to display
        """
        self.status_label.setText(message)
        self.statusBar().showMessage(message)
    
    def closeEvent(self, event) -> None:
        """
        Handle the window close event.
        
        Cleans up resources before closing the application.
        
        Parameters
        ----------
        event : QCloseEvent
            The close event
        """
        # Stop the hotkey listener
        self.controller.stop_listening_for_hotkeys()
        
        # Accept the close event
        event.accept()
