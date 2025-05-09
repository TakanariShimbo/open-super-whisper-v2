"""
Thread Manager Implementation

This module provides a central thread management system for 
safely communicating between threads in a Qt application.
"""

from typing import Callable, Any
import uuid

from PyQt6.QtCore import QObject, pyqtSignal, Qt, QTimer

from .task_worker import TaskWorker


class ThreadManager(QObject):
    """
    A class for managing safe communication and operations between threads
    
    This class provides safe thread-to-thread communication and operations
    based on Qt's thread model.
    """
    
    # Signal definitions
    taskCompleted = pyqtSignal(str, object)  # task_id, result
    taskFailed = pyqtSignal(str, str)        # task_id, error_message
    statusUpdate = pyqtSignal(str, int)      # status_message, timeout_ms
    processingComplete = pyqtSignal(object)  # processing_result
    timerUpdate = pyqtSignal(str)            # time_string
    streamUpdate = pyqtSignal(str)           # stream_chunk
    
    # Internal signals
    _execute_in_main_thread = pyqtSignal(object, tuple, dict)  # func, args, kwargs
    
    def __init__(self) -> None:
        """
        Initialize the ThreadManager
        """
        super().__init__()
        
        # Timer related
        self._recording_timer = None
        self._recording_start_time = 0
        
        # Task related
        self._current_tasks = {}
        
        # Internal signal connections
        self._setup_internal_connections()
    
    def _setup_internal_connections(self) -> None:
        """
        Set up internal signal/slot connections
        """
        # Task completion/error handling
        self.taskCompleted.connect(self._handle_task_completed, Qt.ConnectionType.QueuedConnection)
        self.taskFailed.connect(self._handle_task_failed, Qt.ConnectionType.QueuedConnection)
        
        # Connect main thread execution signal
        self._execute_in_main_thread.connect(self._execute_function, Qt.ConnectionType.QueuedConnection)
    
    def _execute_function(self, func: Callable, args: tuple, kwargs: dict) -> None:
        """
        Execute a function with the given arguments in the main thread.
        
        Parameters
        ----------
        func : Callable
            Function to execute
        args : tuple
            Positional arguments
        kwargs : dict
            Keyword arguments
        """
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"Error in main thread execution: {e}")
    
    def run_in_main_thread(self, func: Callable, *args, delay_ms=0, **kwargs) -> None:
        """
        Run a function in the main thread
        
        Parameters
        ----------
        func : Callable
            Function to execute
        *args
            Positional arguments to pass to the function
        delay_ms : int, optional
            Delay in milliseconds before executing the function
        **kwargs
            Keyword arguments to pass to the function
        """
        if delay_ms > 0:
            # Create a delayed execution using QTimer
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._execute_in_main_thread.emit(func, args, kwargs))
            timer.start(delay_ms)
        else:
            # Execute immediately (through signal for thread safety)
            self._execute_in_main_thread.emit(func, args, kwargs)
    
    def run_in_worker_thread(self, task_id: str, func: Callable, *args, callback=None, **kwargs) -> str:
        """
        Run a function in a worker thread
        
        Parameters
        ----------
        task_id : str
            Task identifier
        func : Callable
            Function to execute
        *args
            Positional arguments to pass to the function
        callback : Optional[Callable], optional
            Function to call with the result when the task completes
        **kwargs
            Keyword arguments to pass to the function
            
        Returns
        -------
        str
            Task ID
        """
        # Generate task ID if not specified
        if not task_id:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # Create and run TaskWorker
        worker = TaskWorker(task_id, func, args, kwargs)
        
        # Connect signals
        def handle_task_completed(tid, result):
            self.taskCompleted.emit(tid, result)
            if callback and tid == task_id:
                # Run callback in main thread for thread safety
                self.run_in_main_thread(callback, result)
        
        worker.taskCompleted.connect(
            handle_task_completed,
            Qt.ConnectionType.QueuedConnection
        )
        worker.taskFailed.connect(
            lambda tid, error: self.taskFailed.emit(tid, error),
            Qt.ConnectionType.QueuedConnection
        )
        
        # Add to current tasks
        self._current_tasks[task_id] = worker
        
        # Start task
        worker.start()
        
        return task_id
    
    def _handle_task_completed(self, task_id: str, result: Any) -> None:
        """
        Handler for task completion
        
        Parameters
        ----------
        task_id : str
            Task ID
        result : Any
            Task result
        """
        # Clean up task
        if task_id in self._current_tasks:
            self._current_tasks[task_id].deleteLater()
            del self._current_tasks[task_id]
    
    def _handle_task_failed(self, task_id: str, error: str) -> None:
        """
        Handler for task errors
        
        Parameters
        ----------
        task_id : str
            Task ID
        error : str
            Error message
        """
        # Clean up task
        if task_id in self._current_tasks:
            self._current_tasks[task_id].deleteLater()
            del self._current_tasks[task_id]
    
    # def update_status(self, message: str, timeout: int = 0) -> None:
    #     """
    #     Safely update the status bar
        
    #     Parameters
    #     ----------
    #     message : str
    #         Message to display
    #     timeout : int, optional
    #         Display time (milliseconds), 0 for persistent display
    #     """
    #     # Emit status update signal
    #     self.statusUpdate.emit(message, timeout)
    
    # def start_recording_timer(self) -> None:
    #     """
    #     Start the recording timer
    #     """
    #     self._recording_start_time = time.time()
        
    #     # Create timer if it doesn't exist
    #     if not self._recording_timer:
    #         self._recording_timer = QTimer(self)
    #         self._recording_timer.timeout.connect(self._update_recording_time)
        
    #     # Start timer
    #     self._recording_timer.start(1000)  # Update every second

    # def stop_recording_timer(self) -> None:
    #     """
    #     Stop the recording timer
    #     """
    #     if self._recording_timer and self._recording_timer.isActive():
    #         self._recording_timer.stop()
    
    # def _update_recording_time(self) -> None:
    #     """
    #     Update recording time
    #     """
    #     # Calculate and display elapsed time
    #     elapsed = int(time.time() - self._recording_start_time)
    #     minutes = elapsed // 60
    #     seconds = elapsed % 60
    #     time_str = f"{minutes:02d}:{seconds:02d}"
        
    #     # Emit timer update signal
    #     self.timerUpdate.emit(time_str)
        
    # def update_stream(self, chunk: str) -> None:
    #     """
    #     Send an LLM streaming update
        
    #     Parameters
    #     ----------
    #     chunk : str
    #         Text chunk from LLM streaming response
    #     """
    #     self.streamUpdate.emit(chunk)
