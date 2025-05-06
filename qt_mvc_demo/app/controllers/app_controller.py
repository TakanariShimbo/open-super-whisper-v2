"""
PyQt6 MVC Application Controller

This module contains the controller component of the MVC architecture.
The AppController class acts as a mediator between the user interface (View)
and the worker threads (Model), implementing the application's business logic.

The controller receives user input from the view, processes it, and updates
the view with results. It manages the creation and execution of background
tasks in separate threads to ensure the UI remains responsive during
long-running operations.

See Also
--------
app.models.thread_manager : Manages worker threads
app.models.task_worker : Implements the worker for background tasks
app.views.main_window : Implements the main application window
"""
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

from ..models.task_worker import TaskWorker
from ..models.thread_manager import ThreadManager

class AppController(QObject):
    """
    Controller class that manages the application's business logic.
    
    This class serves as a mediator between the user interface and worker threads.
    It handles the creation and management of background tasks, and communicates
    with the UI through Qt signals.
    
    Attributes
    ----------
    task_progress : pyqtSignal
        Signal emitted when task progress updates
    task_result : pyqtSignal
        Signal emitted when a task result is available
    task_started : pyqtSignal
        Signal emitted when a task starts
    task_finished : pyqtSignal
        Signal emitted when a task finishes
    thread_manager : ThreadManager
        Manager for worker threads
    worker : Optional[TaskWorker]
        The current task worker instance
    """
    # Signals to communicate with the UI
    task_progress = pyqtSignal(int)
    task_result = pyqtSignal(str)
    task_started = pyqtSignal()
    task_finished = pyqtSignal()
    
    def __init__(self) -> None:
        """
        Initialize the AppController.
        
        Creates a thread manager instance and initializes the worker to None.
        """
        super().__init__()
        
        # Initialize thread manager
        self.thread_manager = ThreadManager()
        
        # Worker will be created when needed and destroyed when finished
        self.worker: Optional[TaskWorker] = None
    
    def execute_background_task(self) -> None:
        """
        Execute a task in a background thread.
        
        Creates a new TaskWorker instance, connects its signals to the controller's
        signals, and starts the worker in a separate thread using the thread manager.
        """
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
    
    def handle_task_completion(self) -> None:
        """
        Handle task completion and clean up resources.
        
        This method is called when a task is completed. It emits the task_finished
        signal and releases the thread resources.
        """
        # Emit task finished signal
        self.task_finished.emit()
        
        # Clean up thread and worker
        self.thread_manager.release_thread_resources()
        self.worker = None
        
    def abort_background_task(self) -> None:
        """
        Abort the currently running task.
        
        If a worker is currently active, this method calls the worker's
        abort_current_task method to stop the task execution. The task
        will then clean up itself through the normal completion handling.
        """
        if self.worker is not None:
            self.worker.abort_current_task()
            self.task_result.emit("Task aborted by user")
