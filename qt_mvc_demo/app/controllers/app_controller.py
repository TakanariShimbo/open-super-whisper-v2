"""
Application controller - business logic layer separate from UI.
"""
from PyQt6.QtCore import QObject, pyqtSignal

from ..models.task_worker import TaskWorker
from ..models.thread_manager import ThreadManager

class AppController(QObject):
    """
    Controller class that manages the application's business logic.
    Serves as a mediator between UI and worker threads.
    """
    # Signals to communicate with the UI
    task_progress = pyqtSignal(int)
    task_result = pyqtSignal(str)
    task_started = pyqtSignal()
    task_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Initialize thread manager
        self.thread_manager = ThreadManager()
        
        # Worker will be created when needed and destroyed when finished
        self.worker = None
    
    def execute_background_task(self):
        """Execute a task in a background thread."""
        # Emit task started signal
        self.task_started.emit()
        
        # Create worker
        self.worker = TaskWorker()
        
        # Connect worker signals to controller signals
        self.worker.progress_updated.connect(self.task_progress.emit)
        self.worker.result_ready.connect(self.task_result.emit)
        self.worker.task_completed.connect(self.handle_task_completion)
        
        # Start worker in a separate thread
        self.thread_manager.run_worker_in_thread(self.worker)
    
    def handle_task_completion(self):
        """Handle task completion and clean up resources."""
        # Emit task finished signal
        self.task_finished.emit()
        
        # Clean up thread and worker
        self.thread_manager.release_thread_resources()
        self.worker = None
