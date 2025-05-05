"""
PyQt6 Thread Manager Module

This module provides a thread management system for PyQt6 applications.
It handles the creation, execution, and proper cleanup of worker threads,
which is essential for creating responsive GUI applications that perform
long-running operations in the background.

The ThreadManager class ensures that worker objects are properly moved
to separate threads and that thread resources are correctly released
when no longer needed, preventing memory leaks and thread-related issues.

Examples
--------
Create a thread manager and run a worker in a thread:

>>> manager = ThreadManager()
>>> worker = MyWorker()  # A QObject subclass with an execute_task method
>>> manager.run_worker_in_thread(worker)
>>> # Later when done
>>> manager.release_thread_resources()

See Also
--------
app.controllers.app_controller : Uses ThreadManager to run tasks
app.models.task_worker : Example worker class to be run in a thread
"""
from typing import Optional
from PyQt6.QtCore import QThread, QObject

class ThreadManager(QObject):
    """
    Manages worker threads to ensure proper thread creation, execution, and cleanup.
    
    This class handles the creation of QThread instances, moves worker objects
    into these threads, and ensures proper cleanup when the threads are no longer
    needed.
    
    Attributes
    ----------
    thread : Optional[QThread]
        The managed QThread instance
    """
    
    def __init__(self) -> None:
        """
        Initialize the ThreadManager.
        
        Creates a new ThreadManager instance with no active thread.
        """
        super().__init__()
        self.thread: Optional[QThread] = None
    
    def run_worker_in_thread(self, worker: QObject) -> None:
        """
        Run a worker object in a new thread.
        
        Creates a new QThread, moves the worker to the thread, connects
        signals and slots, and starts the thread.
        
        Parameters
        ----------
        worker : QObject
            The worker object to be moved to the thread. Must have
            an execute_task method and a task_completed signal.
        """
        # Create a new thread
        self.thread = QThread()
        
        # Move worker to thread
        worker.moveToThread(self.thread)
        
        # Connect thread started signal to worker's execute_task method
        self.thread.started.connect(worker.execute_task)
        
        # Connect worker's finished signal to thread's quit method
        worker.task_completed.connect(self.thread.quit)
        
        # Start the thread
        self.thread.start()
    
    def release_thread_resources(self) -> None:
        """
        Release thread resources and perform cleanup.
        
        This method should be called when the thread is no longer needed.
        It safely terminates the thread if it's running and sets the thread
        reference to None.
        """
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        
        self.thread = None
    
    def __del__(self) -> None:
        """
        Ensure thread is cleaned up when manager is destroyed.
        
        This destructor ensures that thread resources are properly released
        when the ThreadManager instance is garbage collected.
        """
        self.release_thread_resources()
