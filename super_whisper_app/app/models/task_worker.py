"""
Task Worker Module

This module provides the TaskWorker class for executing background tasks
in a separate thread, with progress reporting and task completion signals.
"""

from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class TaskWorker(QObject):
    """
    Worker class for executing background tasks.
    
    This class executes tasks in a separate thread, and provides signals
    for reporting progress and completion of the task.
    
    Attributes
    ----------
    progress_updated : pyqtSignal
        Signal emitted when task progress updates (int value 0-100)
    result_ready : pyqtSignal
        Signal emitted when task produces a result (str)
    task_completed : pyqtSignal
        Signal emitted when task is completed
    """
    
    # Signals
    progress_updated = pyqtSignal(int)
    result_ready = pyqtSignal(str)
    task_completed = pyqtSignal()
    
    def __init__(self) -> None:
        """
        Initialize the TaskWorker.
        
        Sets up the initial state and connects signals/slots.
        """
        super().__init__()
        
        # Task state
        self._abort_requested = False
        self._step_timer = QTimer()
        self._step_timer.timeout.connect(self._perform_task_step)
        self._current_step = 0
        self._total_steps = 10  # Example value
    
    def start_task(self) -> None:
        """
        Start executing the task.
        
        This method is called when the thread is started.
        """
        # Reset state
        self._abort_requested = False
        self._current_step = 0
        
        # Emit initial progress
        self.progress_updated.emit(0)
        
        # Start timer for task steps
        self._step_timer.start(300)  # 300ms per step
    
    def _perform_task_step(self) -> None:
        """
        Perform a single step of the task.
        
        This method is called on each timer tick, and performs
        one step of the task, updating progress and checking for
        abort requests.
        """
        # Check if abort was requested
        if self._abort_requested:
            self._finish_task()
            return
        
        # Increment step
        self._current_step += 1
        
        # Calculate progress percentage
        progress = int((self._current_step / self._total_steps) * 100)
        self.progress_updated.emit(progress)
        
        # Simulate task work
        self.result_ready.emit(f"Processing step {self._current_step}/{self._total_steps}")
        
        # Check if task is complete
        if self._current_step >= self._total_steps:
            self.result_ready.emit("Task completed successfully!")
            self._finish_task()
    
    def _finish_task(self) -> None:
        """
        Finish task execution.
        
        Stops the timer and emits the task_completed signal.
        """
        # Stop timer
        self._step_timer.stop()
        
        # Emit final progress and completion signal
        self.progress_updated.emit(100)
        self.task_completed.emit()
    
    def abort_current_task(self) -> None:
        """
        Abort the currently running task.
        
        Sets the abort flag so the task will stop on the next step.
        """
        self._abort_requested = True
