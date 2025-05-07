"""
Thread Manager Module

This module provides the ThreadManager class for managing worker threads
to ensure that long-running operations don't block the UI.
"""

from typing import Callable, Any, Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class WorkerThread(QThread):
    """
    Worker thread for executing long-running tasks.
    
    This class provides a thread that can execute a task without
    blocking the main UI thread, and can signal when the task is complete.
    """
    task_completed = pyqtSignal(object)
    
    def __init__(self, task: Callable, *args, **kwargs):
        """
        Initialize a worker thread.
        
        Parameters
        ----------
        task : Callable
            The function to execute in the thread
        *args, **kwargs
            Arguments to pass to the task function
        """
        super().__init__()
        self._task = task
        self._args = args
        self._kwargs = kwargs
        self._aborted = False
        
    def abort_task(self):
        """
        Abort the current task.
        
        Sets a flag that can be checked by the task to abort early.
        """
        self._aborted = True
        
    def is_aborted(self) -> bool:
        """
        Check if the task has been aborted.
        
        Returns
        -------
        bool
            True if the task has been aborted, False otherwise
        """
        return self._aborted
    
    def run(self):
        """
        Run the task.
        
        Executes the task function with the provided arguments
        and emits the task_completed signal with the result.
        """
        try:
            result = self._task(*self._args, **self._kwargs)
            self.task_completed.emit(result)
        except Exception as e:
            # Emit exception as result for handling by caller
            self.task_completed.emit(e)


class ThreadManager(QObject):
    """
    Manager for worker threads.
    
    This class provides methods for running tasks in worker threads
    and manages the lifecycle of the threads.
    """
    
    def __init__(self):
        """
        Initialize the ThreadManager.
        """
        super().__init__()
        self._threads = {}
        
    def run_worker_in_thread(self, worker: QObject) -> None:
        """
        Run a worker object in a separate thread.
        
        Parameters
        ----------
        worker : QObject
            The worker object to run in a thread
        """        
        # Check if a previous thread exists and clean it up first
        if "worker" in self._threads:
            old_thread, old_worker = self._threads["worker"]
            
            if old_thread.isRunning():
                # Disconnect any old connections to ensure the thread can terminate properly
                try:
                    if old_worker and hasattr(old_worker, 'deleteLater'):
                        old_worker.deleteLater()
                except Exception as e:
                    pass
                
                # Try to quit the thread gracefully
                old_thread.quit()
                if not old_thread.wait(1000):  # Wait up to 1 second for thread to finish
                    old_thread.terminate()
                    old_thread.wait(1000)
            
            # Clear the old reference
            del self._threads["worker"]
        
        # Create new thread
        thread = QThread()
        
        # Connect finished signal to cleanup
        thread.finished.connect(lambda: self._thread_finished("worker"))
        
        # Move worker to the thread
        worker.moveToThread(thread)
        
        # Connect thread-specific signals/slots
        thread.started.connect(worker.start_task)
        
        # Store thread and worker
        self._threads["worker"] = (thread, worker)
        
        # Start thread
        thread.start()

    def _thread_finished(self, thread_id: str) -> None:
        """
        Handle thread finished event.
        
        Parameters
        ----------
        thread_id : str
            ID of the thread that finished
        """
        # Remove the thread from the threads dict if it's still there
        if thread_id in self._threads:
            thread, worker = self._threads[thread_id]
            
            # Delete the worker
            if worker and hasattr(worker, 'deleteLater'):
                try:
                    worker.deleteLater()
                except Exception as e:
                    pass
            
            # Remove from dict
            del self._threads[thread_id]
        
    def run_task_in_thread(self, task_id: str, task_func: Callable, 
                         *args, callback: Optional[Callable[[Any], None]] = None, 
                         **kwargs) -> None:
        """
        Run a task function in a worker thread.
        
        Parameters
        ----------
        task_id : str
            Identifier for the task
        task_func : Callable
            The function to execute in the thread
        *args
            Arguments to pass to the task function
        callback : Optional[Callable[[Any], None]], optional
            Callback function to call with the result, by default None
        **kwargs
            Keyword arguments to pass to the task function
        """
        # Create worker thread
        worker = WorkerThread(task_func, *args, **kwargs)
        
        # Connect completion signal
        if callback:
            worker.task_completed.connect(callback)
        
        # Store thread
        if task_id in self._threads:
            # Clean up existing thread first
            old_thread, _ = self._threads[task_id]
            if old_thread.isRunning():
                old_thread.quit()
                old_thread.wait()
                
        self._threads[task_id] = (worker, None)
        
        # Start thread
        worker.start()
    
    def abort_task(self, task_id: str) -> bool:
        """
        Abort a running task.
        
        Parameters
        ----------
        task_id : str
            Identifier for the task to abort
            
        Returns
        -------
        bool
            True if the task was aborted, False if the task was not found
        """
        if task_id in self._threads:
            thread, worker = self._threads[task_id]
            
            if isinstance(thread, WorkerThread):
                thread.abort_task()
                return True
            elif worker is not None:
                # Try to call abort_task on worker
                if hasattr(worker, 'abort_task') and callable(getattr(worker, 'abort_task')):
                    worker.abort_task()
                    return True
                    
        return False
        
    def release_thread_resources(self, task_id: Optional[str] = None) -> None:
        """
        Release thread resources.
        
        Parameters
        ----------
        task_id : Optional[str], optional
            Identifier for a specific task, or None to release all, by default None
        """
        if task_id:
            # Release specific thread
            if task_id in self._threads:
                thread, _ = self._threads[task_id]
                
                if thread.isRunning():
                    thread.quit()
                    thread.wait()
                    
                del self._threads[task_id]
        else:
            # Release all threads
            for thread, _ in self._threads.values():
                if thread.isRunning():
                    thread.quit()
                    thread.wait()
                    
            self._threads.clear()
