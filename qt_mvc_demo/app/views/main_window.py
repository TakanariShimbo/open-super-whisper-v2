"""
PyQt6 Main Window Module

This module implements the main window component of the MVC architecture.
It defines the user interface elements and connects UI events to the
appropriate controller methods.

The MainWindow class represents the "View" in the MVC pattern, responsible
for displaying information to the user and capturing user input. It does not
contain business logic but delegates tasks to the controller.

The window provides an interface for starting background tasks, displaying
progress, and showing results from the task execution. It demonstrates
proper UI/logic separation and thread management in PyQt6 applications.

The window now supports minimizing to system tray, allowing the application
to run in the background while maintaining accessibility through the system tray.
"""

import os
import sys

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QProgressBar, QTextEdit, QMessageBox, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, pyqtSlot, QEvent
from PyQt6.QtGui import QCloseEvent

from ..controllers.app_controller import AppController
from .tray.system_tray import SystemTray

class MainWindow(QMainWindow):
    """
    Main application window with UI elements.
    
    This class represents the main window of the application. It contains
    the UI components and connects to the application controller to handle
    user interactions and display task progress and results.
    
    Attributes
    ----------
    controller : AppController
        The application controller that manages the business logic
    start_button : QPushButton
        Button to start the background task
    abort_button : QPushButton
        Button to abort the running background task
    progress_bar : QProgressBar
        Progress indicator for the background task
    status_label : QLabel
        Label showing the current status of the application
    results_area : QTextEdit
        Text area to display task results
    system_tray : SystemTray
        System tray icon for background operation
    is_closing : bool
        Flag to track if the application is actually closing or just minimizing to tray
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
        self.controller = AppController()
        
        # Connect signals from controller to UI slots
        self.controller.task_progress.connect(self.update_progress_indicator)
        self.controller.task_result.connect(self.append_result_to_log)
        self.controller.task_started.connect(self.handle_task_start_event)
        self.controller.task_finished.connect(self.handle_task_completion_event)
        
        # Initialize system tray
        self.setup_system_tray()
        
        # Track if window is actually closing
        self.is_closing = False
        
    def setup_user_interface(self) -> None:
        """
        Setup and initialize the user interface components.
        
        Creates and configures all UI components including the window layout,
        title, buttons, progress bar, status label, and results area.
        """
        # Set window properties
        self.setWindowTitle("PyQt6 Thread Demo")
        self.setMinimumSize(500, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add title label
        title_label = QLabel("Thread Management Demo")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Add description
        description = QLabel(
            "This demo shows how to manage threads in PyQt6 applications.\n"
            "Click 'Start Task' to run a simulated long-running process in a background thread.\n"
            "You can click 'Abort Task' to cancel the running process at any time.\n"
            "Closing the window will minimize to system tray."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add start button
        self.start_button = QPushButton("Start Task")
        self.start_button.clicked.connect(self.handle_start_button_click)
        layout.addWidget(self.start_button)
        
        # Add abort button
        self.abort_button = QPushButton("Abort Task")
        self.abort_button.clicked.connect(self.handle_abort_button_click)
        self.abort_button.setEnabled(False)  # Disabled initially
        layout.addWidget(self.abort_button)
        
        # Add quit button
        self.quit_button = QPushButton("Quit Application")
        self.quit_button.clicked.connect(self.handle_quit_button_click)
        layout.addWidget(self.quit_button)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Add status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Add results area
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)
    
    def setup_system_tray(self) -> None:
        """
        Setup the system tray icon.
        
        Creates the system tray icon and connects signals to slots for
        showing/hiding the window and quitting the application.
        """
        # Get icon path
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "assets", "icon.png"
        )
        
        # Create system tray
        self.system_tray = SystemTray(icon_path)
        
        # Connect signals
        self.system_tray.show_window_signal.connect(self.show_window)
        self.system_tray.hide_window_signal.connect(self.hide_window)
        self.system_tray.quit_application_signal.connect(self.handle_quit_button_click)
        
        # Show system tray icon
        self.system_tray.show()
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the window close event.
        
        This method is called when the user attempts to close the window.
        It intercepts the close event to minimize to system tray instead of
        actually closing the application, unless explicitly quit.
        
        Parameters
        ----------
        event : QCloseEvent
            The close event to handle
        """
        if not self.is_closing:
            event.ignore()
            self.hide_window()
            
            # Show a message the first time
            self.system_tray.showMessage(
                "Application Minimized",
                "The application is still running in the background. "
                "Click the tray icon to restore.",
                QSystemTrayIcon.MessageIcon.NoIcon,
                3000
            )
        else:
            # Actually close
            event.accept()
    
    @pyqtSlot()
    def handle_start_button_click(self) -> None:
        """
        Handle when the start button is clicked by the user.
        
        Delegates to the controller to start the background task.
        """
        self.controller.execute_background_task()
    
    @pyqtSlot()
    def handle_abort_button_click(self) -> None:
        """
        Handle when the abort button is clicked by the user.
        
        Delegates to the controller to abort the current background task.
        """
        self.controller.abort_background_task()
    
    @pyqtSlot()
    def handle_quit_button_click(self) -> None:
        """
        Handle when the quit button is clicked by the user.
        
        Shows a confirmation dialog and if confirmed, sets the closing flag
        and closes the application.
        """
        reply = QMessageBox.question(
            self, 
            'Quit Application',
            'Are you sure you want to quit the application?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.is_closing = True
            self.close()
            sys.exit(0)
    
    @pyqtSlot(int)
    def update_progress_indicator(self, value: int) -> None:
        """
        Update the progress bar indicator with current task progress value.
        
        Parameters
        ----------
        value : int
            The progress value (0-100) to display in the progress bar
        """
        self.progress_bar.setValue(value)
    
    @pyqtSlot(str)
    def append_result_to_log(self, result: str) -> None:
        """
        Append the task result to the log display area.
        
        Parameters
        ----------
        result : str
            The text result to append to the log
        """
        self.results_area.append(result)
    
    @pyqtSlot()
    def handle_task_start_event(self) -> None:
        """
        Handle the event when a task is started.
        
        Updates the UI to reflect that a task is in progress by disabling
        the start button, enabling the abort button, updating the status label,
        and resetting the progress bar.
        """
        self.start_button.setEnabled(False)
        self.abort_button.setEnabled(True)  # Enable abort button when task starts
        self.status_label.setText("Task is running...")
        self.progress_bar.setValue(0)
    
    @pyqtSlot()
    def handle_task_completion_event(self) -> None:
        """
        Handle the event when a task is completed.
        
        Updates the UI to reflect that a task is completed by enabling
        the start button, disabling the abort button, updating the status label,
        and setting the progress bar to 100%.
        """
        self.start_button.setEnabled(True)
        self.abort_button.setEnabled(False)  # Disable abort button when task completes
        self.status_label.setText("Task completed")
        self.progress_bar.setValue(100)
    
    @pyqtSlot()
    def show_window(self) -> None:
        """
        Show and activate the application window.
        
        This method is called when the user clicks the tray icon or selects
        'Show Window' from the tray menu.
        """
        self.showNormal()
        self.activateWindow()
    
    @pyqtSlot()
    def hide_window(self) -> None:
        """
        Hide the application window.
        
        This method is called when the user selects 'Hide Window' from the
        tray menu or closes the window.
        """
        self.hide()
