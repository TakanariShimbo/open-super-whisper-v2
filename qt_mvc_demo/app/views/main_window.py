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

Examples
--------
Creating and showing the main window:

>>> app = QApplication(sys.argv)
>>> window = MainWindow()
>>> window.show()
>>> sys.exit(app.exec())

See Also
--------
app.controllers.app_controller : The controller used by this view
app.models.thread_manager : Manages the worker threads
app.models.task_worker : Implements the background task
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSlot

from ..controllers.app_controller import AppController

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
    progress_bar : QProgressBar
        Progress indicator for the background task
    status_label : QLabel
        Label showing the current status of the application
    results_area : QTextEdit
        Text area to display task results
    """
    
    def __init__(self) -> None:
        """
        Initialize the MainWindow.
        
        Sets up the user interface and connects signals from the controller
        to UI slots.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
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
        
    def setup_user_interface(self) -> None:
        """
        Setup and initialize the user interface components.
        
        Creates and configures all UI components including the window layout,
        title, buttons, progress bar, status label, and results area.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
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
            "Click 'Start Task' to run a simulated long-running process in a background thread."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add start button
        self.start_button = QPushButton("Start Task")
        self.start_button.clicked.connect(self.handle_start_button_click)
        layout.addWidget(self.start_button)
        
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
    
    @pyqtSlot()
    def handle_start_button_click(self) -> None:
        """
        Handle when the start button is clicked by the user.
        
        Delegates to the controller to start the background task.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        """
        self.controller.execute_background_task()
    
    @pyqtSlot(int)
    def update_progress_indicator(self, value: int) -> None:
        """
        Update the progress bar indicator with current task progress value.
        
        Parameters
        ----------
        value : int
            The progress value (0-100) to display in the progress bar
        
        Returns
        -------
        None
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
        
        Returns
        -------
        None
        """
        self.results_area.append(result)
    
    @pyqtSlot()
    def handle_task_start_event(self) -> None:
        """
        Handle the event when a task is started.
        
        Updates the UI to reflect that a task is in progress by disabling
        the start button, updating the status label, and resetting the progress bar.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        """
        self.start_button.setEnabled(False)
        self.status_label.setText("Task is running...")
        self.progress_bar.setValue(0)
    
    @pyqtSlot()
    def handle_task_completion_event(self) -> None:
        """
        Handle the event when a task is completed.
        
        Updates the UI to reflect that a task is completed by enabling
        the start button, updating the status label, and setting the progress
        bar to 100%.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        """
        self.start_button.setEnabled(True)
        self.status_label.setText("Task completed")
        self.progress_bar.setValue(100)
