"""
Task Worker Implementation

This module provides a worker class for executing long-running tasks
in a separate thread, with proper signal handling for task completion
and failures.
"""

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from typing import Callable, Dict, Any, Tuple

class TaskWorker(QThread):
    """
    Worker class for processing long-running tasks
    
    This class inherits from QThread to execute functions in a separate thread
    and notify results via signals.
    """
    
    # Signal definitions
    taskCompleted = pyqtSignal(str, object)  # task_id, result
    taskFailed = pyqtSignal(str, str)       # task_id, error_message
    
    def __init__(self, task_id: str, func: Callable, args: Tuple, kwargs: Dict[str, Any]):
        """
        Initialize TaskWorker
        
        Parameters
        ----------
        task_id : str
            Task identifier
        func : Callable
            Function to execute
        args : Tuple
            Positional arguments for the function
        kwargs : Dict[str, Any]
            Keyword arguments for the function
        """
        super().__init__()
        
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self) -> None:
        """
        Thread execution process
        
        Executes the function and notifies results or errors via signals.
        """
        try:
            # Execute function
            result = self.func(*self.args, **self.kwargs)
            
            # Emit completion signal
            self.taskCompleted.emit(self.task_id, result)
            
        except Exception as e:
            # Emit error signal
            error_msg = f"Error in task {self.task_id}: {str(e)}"
            print(error_msg)
            self.taskFailed.emit(self.task_id, str(e))
