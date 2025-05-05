"""
Task worker for handling long-running operations in a separate thread.
"""
import time
import random
from PyQt6.QtCore import QObject, pyqtSignal

class TaskWorker(QObject):
    """
    Worker class that performs a task in a separate thread.
    Emits signals to communicate with the controller.
    """
    # Define signals for communication
    progress_updated = pyqtSignal(int)
    result_ready = pyqtSignal(str)
    task_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # Initialize any worker-specific variables here
        self._is_running = False
    
    def run(self):
        """
        Main worker method that will be executed in a separate thread.
        Simulates a long-running task with progress updates.
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
    
    def cancel(self):
        """Cancel the running task."""
        self._is_running = False
