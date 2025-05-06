"""
PyQt6 Task Worker Module

This module provides a worker class for executing long-running tasks in 
separate threads within PyQt6 applications. Using worker threads ensures 
that the UI remains responsive while intensive operations are performed 
in the background.

The TaskWorker class simulates a time-consuming operation that reports
progress and produces results. It demonstrates proper communication between
threads using Qt's signal and slot mechanism, which is thread-safe and
avoids common threading pitfalls.
"""
import time
import random

from PyQt6.QtCore import QObject, pyqtSignal


class TaskWorker(QObject):
    """
    Worker class that performs a task in a separate thread.
    
    This class is designed to be moved to a separate thread and performs
    a simulated long-running task. It communicates with the controller
    using Qt signals.
    
    Attributes
    ----------
    progress_updated : pyqtSignal
        Signal emitted when the task progress updates (0-100%)
    result_ready : pyqtSignal
        Signal emitted when a result from the task is available
    task_completed : pyqtSignal
        Signal emitted when the task is fully completed
    _is_running : bool
        Internal flag to track if the task is currently running
    """
    # Define signals for communication
    progress_updated = pyqtSignal(int)
    result_ready = pyqtSignal(str)
    task_completed = pyqtSignal()
    
    def __init__(self) -> None:
        """
        Initialize the TaskWorker.
        
        Creates a new TaskWorker instance and initializes the running flag to False.
        """
        super().__init__()
        # Initialize worker-specific variables
        self._is_running: bool = False
    
    def execute_task(self) -> None:
        """
        Execute the task in a separate thread.
        
        This method simulates a long-running task with progress updates.
        It processes 10 steps, updates the progress after each step, and
        emits results. The method is designed to be executed in a separate thread.
        """
        self._is_running = True
        
        # Simulate task initialization
        self.result_ready.emit("Task started...")
        time.sleep(0.5)  # Simulate initialization time
        
        # Simulate a task with 10 steps
        for step in range(10):
            # Check if task was cancelled
            if not self._is_running:
                break
            
            # Update progress (0-100%)
            progress = (step + 1) * 10
            self.progress_updated.emit(progress)
            
            # Simulate work for this step
            processing_time = random.uniform(0.3, 1.0)
            time.sleep(processing_time)
            
            # Generate a result for this step
            result = f"Step {step + 1} completed in {processing_time:.2f} seconds"
            self.result_ready.emit(result)
        
        # Emit final result
        if self._is_running:
            self.result_ready.emit("All steps completed successfully!")
        
        # Signal that the task is completed
        self.task_completed.emit()
        self._is_running = False
    
    def abort_current_task(self) -> None:
        """
        Abort the currently running task immediately.
        
        Sets the _is_running flag to False, which will cause the execute_task
        method to exit its processing loop at the next iteration.
        """
        self._is_running = False
