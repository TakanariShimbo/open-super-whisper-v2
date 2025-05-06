"""
PyQt6 MVC Application Controller

This module contains the controller component of the MVC architecture.
The AppController class acts as a mediator between the user interface (View)
and the worker threads (Model), implementing the application's business logic.

The controller receives user input from the view, processes it, and updates
the view with results. It manages the creation and execution of background
tasks in separate threads to ensure the UI remains responsive during
long-running operations.

The controller also manages global hotkeys for starting and stopping tasks
through the HotkeyModel, allowing users to control tasks even when the
application is in the background.
"""
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from ..models.task_worker import TaskWorker
from ..models.thread_manager import ThreadManager
from ..models.hotkey_manager import HotkeyModel


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
    hotkey_changed : pyqtSignal
        Signal emitted when the task hotkey is changed
    _thread_manager : ThreadManager
        Manager for worker threads
    _worker : Optional[TaskWorker]
        The current task worker instance
    _hotkey_model : HotkeyModel
        Model for managing application hotkeys
    """
    # Signals to communicate with the UI
    task_progress = pyqtSignal(int)
    task_result = pyqtSignal(str)
    task_started = pyqtSignal()
    task_finished = pyqtSignal()
    hotkey_changed = pyqtSignal(str)  # Emitted when hotkey changes
    
    def __init__(self) -> None:
        """
        Initialize the AppController.
        
        Creates a thread manager instance and initializes the worker to None.
        Also initializes the hotkey model for managing global hotkeys.
        """
        super().__init__()
        
        # Initialize thread manager
        self._thread_manager = ThreadManager()
        
        # Worker will be created when needed and destroyed when finished
        self._worker: Optional[TaskWorker] = None
        
        # Initialize hotkey model
        self._hotkey_model = HotkeyModel()
        
        # Connect hotkey signal to handler
        self._hotkey_model.hotkey_triggered.connect(self._handle_hotkey_triggered)
    
    def execute_background_task(self) -> None:
        """
        Execute a task in a background thread.
        
        Creates a new TaskWorker instance, connects its signals to the controller's
        signals, and starts the worker in a separate thread using the thread manager.
        """
        # Emit task started signal
        self.task_started.emit()
        
        # Create worker
        self._worker = TaskWorker()
        
        # Connect worker signals to controller signals
        self._worker.progress_updated.connect(self.task_progress.emit)
        self._worker.result_ready.connect(self.task_result.emit)
        self._worker.task_completed.connect(self.handle_task_completion)
        
        # Start worker in a separate thread
        self._thread_manager.run_worker_in_thread(self._worker)
    
    def handle_task_completion(self) -> None:
        """
        Handle task completion and clean up resources.
        
        This method is called when a task is completed. It emits the task_finished
        signal and releases the thread resources.
        """
        # Emit task finished signal
        self.task_finished.emit()
        
        # Clean up thread and worker
        self._thread_manager.release_thread_resources()
        self._worker = None
        
    def abort_background_task(self) -> None:
        """
        Abort the currently running task.
        
        If a worker is currently active, this method calls the worker's
        abort_current_task method to stop the task execution. The task
        will then clean up itself through the normal completion handling.
        """
        if self._worker is not None:
            self._worker.abort_current_task()
            self.task_result.emit("Task aborted by user")
    
    def toggle_task(self) -> None:
        """
        Toggle the task state.
        
        If a task is running, stop it. If no task is running, start one.
        This is mainly used for hotkey control.
        """
        if self._worker is not None:
            self.abort_background_task()
        else:
            self.execute_background_task()
    
    @pyqtSlot(str)
    def _handle_hotkey_triggered(self, hotkey: str) -> None:
        """
        Handle hotkey trigger event from the hotkey model.
        
        Parameters
        ----------
        hotkey : str
            The hotkey that was triggered
        """
        # If this is our task hotkey, toggle the task
        if hotkey == self._hotkey_model.task_hotkey:
            self.toggle_task()
    
    def set_task_hotkey(self, hotkey: str) -> bool:
        """
        Set the hotkey for controlling tasks.
        
        Parameters
        ----------
        hotkey : str
            The hotkey string to set
            
        Returns
        -------
        bool
            True if the hotkey was set successfully, False otherwise
        """
        # Validate the hotkey
        if not hotkey or not self._hotkey_model.is_valid_hotkey(hotkey):
            return False
            
        # Set the hotkey in the model
        self._hotkey_model.task_hotkey = hotkey
        
        # Emit signal about the hotkey change
        self.hotkey_changed.emit(hotkey)
        
        return True
    
    def get_task_hotkey(self) -> str:
        """
        Get the current task hotkey.
        
        Returns
        -------
        str
            The current task hotkey or empty string if not set
        """
        return self._hotkey_model.task_hotkey or ""
