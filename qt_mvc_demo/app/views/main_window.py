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

The window features a unified task control button that changes its text and
function based on the application state - showing "Start Task" when no task 
is running and "Abort Task" during task execution. This approach simplifies 
the UI while maintaining full functionality.

The implementation includes protection against button spamming (rapid clicking)
through a state management system that prevents multiple simultaneous requests
from being processed. This ensures that task operations are atomic and prevents
race conditions that could occur when clicking the button rapidly.

The window also supports minimizing to system tray, allowing the application
to run in the background while maintaining accessibility through the system tray.
"""

import os
import sys

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QProgressBar, QTextEdit, QMessageBox, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QCloseEvent

from .tray.system_tray import SystemTray
from ..controllers.app_controller import AppController


class MainWindow(QMainWindow):
    """
    Main application window with UI elements.
    
    This class represents the main window of the application. It contains
    the UI components and connects to the application controller to handle
    user interactions and display task progress and results.
    
    Attributes
    ----------
    _controller : AppController
        The application controller that manages the business logic
    _task_button : QPushButton
        Unified button to start or abort the background task, changes text based on state
    _progress_bar : QProgressBar
        Progress indicator for the background task
    _status_label : QLabel
        Label showing the current status of the application
    _results_area : QTextEdit
        Text area to display task results
    _system_tray : SystemTray
        System tray icon for background operation
    _is_closing : bool
        Flag to track if the application is actually closing or just minimizing to tray
    _is_operation_in_progress : bool
        Flag to prevent button spamming and ensure operation atomicity
    """
    
    def __init__(self) -> None:
        """
        Initialize the MainWindow.
        
        Sets up the user interface and connects signals from the controller
        to UI slots.
        """
        super().__init__()
        
        # Initialize UI
        self._setup_user_interface()
        
        # Initialize controller (business logic)
        self._controller = AppController()
        
        # Connect signals from controller to UI slots
        self._controller.task_progress.connect(self._update_progress_indicator)
        self._controller.task_result.connect(self._append_result_to_log)
        self._controller.task_started.connect(self._handle_task_start_event)
        self._controller.task_finished.connect(self._handle_task_completion_event)
        
        # Initialize system tray
        self._setup_system_tray()
        
        # Track if window is actually closing
        self._is_closing = False
        
        # Flag to prevent button spamming and ensure operation atomicity
        self._is_operation_in_progress = False
        
    def _setup_user_interface(self) -> None:
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
            "The button will change to 'Abort Task' when a task is running, allowing you to cancel it.\n"
            "The application is protected against button spamming (rapid clicking).\n"
            "Closing the window will minimize to system tray."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add unified task control button
        self._task_button = QPushButton("Start Task")
        self._task_button.clicked.connect(self._handle_task_button_click)
        layout.addWidget(self._task_button)
        
        # Add quit button
        self._quit_button = QPushButton("Quit Application")
        self._quit_button.clicked.connect(self._handle_quit_button_click)
        layout.addWidget(self._quit_button)
        
        # Add progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)
        
        # Add status label
        self._status_label = QLabel("Ready")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)
        
        # Add results area
        self._results_area = QTextEdit()
        self._results_area.setReadOnly(True)
        layout.addWidget(self._results_area)
    
    def _setup_system_tray(self) -> None:
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
        self._system_tray = SystemTray(icon_path)
        
        # Connect signals
        self._system_tray.show_window_signal.connect(self._show_window)
        self._system_tray.hide_window_signal.connect(self._hide_window)
        self._system_tray.quit_application_signal.connect(self._handle_quit_button_click)
        
        # Show system tray icon
        self._system_tray.show()
    
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
        if not self._is_closing:
            event.ignore()
            self._hide_window()
            
            # Show a message the first time
            self._system_tray.showMessage(
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
    def _handle_task_button_click(self) -> None:
        """
        Handle when the task button is clicked by the user.
        
        Depending on the current state of the application, this will either
        start a new task or abort the currently running task. Implements
        debouncing to prevent rapid button clicking (button spamming) from
        causing unintended behavior.
        """
        # Skip if an operation is already in progress
        if self._is_operation_in_progress:
            # Log message to inform user
            self._append_result_to_log("Please wait, operation in progress...")
            return
            
        # Set operation flag to prevent multiple rapid clicks
        self._is_operation_in_progress = True
        
        # Disable button immediately to provide visual feedback
        self._task_button.setEnabled(False)
        
        # Get the current button text to determine what action to take
        if self._task_button.text() == "Start Task":
            # Update UI immediately for better responsiveness
            self._status_label.setText("Starting task...")
            
            # If showing "Start Task", then start a new task
            self._controller.execute_background_task()
        else:
            # Update UI immediately for better responsiveness
            self._status_label.setText("Aborting task...")
            
            # If showing "Abort Task", then abort the current task
            self._controller.abort_background_task()
    
    @pyqtSlot()
    def _handle_quit_button_click(self) -> None:
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
            self._is_closing = True
            self.close()
            sys.exit(0)
    
    @pyqtSlot(int)
    def _update_progress_indicator(self, value: int) -> None:
        """
        Update the progress bar indicator with current task progress value.
        
        Parameters
        ----------
        value : int
            The progress value (0-100) to display in the progress bar
        """
        self._progress_bar.setValue(value)
    
    @pyqtSlot(str)
    def _append_result_to_log(self, result: str) -> None:
        """
        Append the task result to the log display area.
        
        Parameters
        ----------
        result : str
            The text result to append to the log
        """
        self._results_area.append(result)
    
    @pyqtSlot()
    def _handle_task_start_event(self) -> None:
        """
        Handle the event when a task is started.
        
        Updates the UI to reflect that a task is in progress by changing
        the task button text to "Abort Task", updating the status label,
        and resetting the progress bar. Re-enables the button to allow
        abortion of the running task.
        """
        self._task_button.setText("Abort Task")
        self._status_label.setText("Task is running...")
        self._progress_bar.setValue(0)
        
        # Re-enable the button to allow for task abortion
        self._task_button.setEnabled(True)
        
        # Operation has transitioned to running state, so we reset the flag
        self._is_operation_in_progress = False
    
    @pyqtSlot()
    def _handle_task_completion_event(self) -> None:
        """
        Handle the event when a task is completed.
        
        Updates the UI to reflect that a task is completed by changing
        the task button text to "Start Task", updating the status label,
        and setting the progress bar to 100%. Re-enables the button and
        resets operation flags.
        """
        self._task_button.setText("Start Task")
        self._status_label.setText("Task completed")
        self._progress_bar.setValue(100)
        
        # Re-enable button for next operation
        self._task_button.setEnabled(True)
        
        # Reset operation flag to allow new operations
        self._is_operation_in_progress = False
    
    @pyqtSlot()
    def _show_window(self) -> None:
        """
        Show and activate the application window.
        
        This method is called when the user clicks the tray icon or selects
        'Show Window' from the tray menu.
        """
        self.showNormal()
        self.activateWindow()
    
    @pyqtSlot()
    def _hide_window(self) -> None:
        """
        Hide the application window.
        
        This method is called when the user selects 'Hide Window' from the
        tray menu or closes the window.
        """
        self.hide()
