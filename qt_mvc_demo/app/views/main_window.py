"""
Main application window UI component.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSlot

from ..controllers.app_controller import AppController

class MainWindow(QMainWindow):
    """Main application window with UI elements."""
    
    def __init__(self):
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
        
    def setup_user_interface(self):
        """Setup and initialize the user interface components."""
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
    def handle_start_button_click(self):
        """Handle when the start button is clicked by the user."""
        self.controller.execute_background_task()
    
    @pyqtSlot(int)
    def update_progress_indicator(self, value):
        """Update the progress bar indicator with current task progress value."""
        self.progress_bar.setValue(value)
    
    @pyqtSlot(str)
    def append_result_to_log(self, result):
        """Append the task result to the log display area."""
        self.results_area.append(result)
    
    @pyqtSlot()
    def handle_task_start_event(self):
        """Handle the event when a task is started."""
        self.start_button.setEnabled(False)
        self.status_label.setText("Task is running...")
        self.progress_bar.setValue(0)
    
    @pyqtSlot()
    def handle_task_completion_event(self):
        """Handle the event when a task is completed."""
        self.start_button.setEnabled(True)
        self.status_label.setText("Task completed")
        self.progress_bar.setValue(100)
