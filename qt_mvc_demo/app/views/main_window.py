"""
Main application window UI component.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSlot

from app.controllers.app_controller import AppController

class MainWindow(QMainWindow):
    """Main application window with UI elements."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize UI
        self.init_ui()
        
        # Initialize controller (business logic)
        self.controller = AppController()
        
        # Connect signals from controller to UI slots
        self.controller.task_progress.connect(self.update_progress)
        self.controller.task_result.connect(self.display_result)
        self.controller.task_started.connect(self.on_task_started)
        self.controller.task_finished.connect(self.on_task_finished)
        
    def init_ui(self):
        """Initialize the user interface."""
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
        self.start_button.clicked.connect(self.on_start_clicked)
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
    def on_start_clicked(self):
        """Handle start button click."""
        self.controller.start_task()
    
    @pyqtSlot(int)
    def update_progress(self, value):
        """Update progress bar with current progress value."""
        self.progress_bar.setValue(value)
    
    @pyqtSlot(str)
    def display_result(self, result):
        """Display result in the results area."""
        self.results_area.append(result)
    
    @pyqtSlot()
    def on_task_started(self):
        """Handle task started event."""
        self.start_button.setEnabled(False)
        self.status_label.setText("Task is running...")
        self.progress_bar.setValue(0)
    
    @pyqtSlot()
    def on_task_finished(self):
        """Handle task finished event."""
        self.start_button.setEnabled(True)
        self.status_label.setText("Task completed")
        self.progress_bar.setValue(100)
