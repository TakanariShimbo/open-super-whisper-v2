"""
Thread manager for handling QThread creation and cleanup.
"""
from PyQt6.QtCore import QThread, QObject

class ThreadManager(QObject):
    """
    Manages worker threads to ensure proper thread creation,
    execution, and cleanup.
    """
    
    def __init__(self):
        super().__init__()
        self.thread = None
    
    def start_worker(self, worker):
        """
        Start a worker in a new thread.
        
        Args:
            worker: The worker object to be moved to the thread
        """
        # Create a new thread
        self.thread = QThread()
        
        # Move worker to thread
        worker.moveToThread(self.thread)
        
        # Connect thread started signal to worker's run method
        self.thread.started.connect(worker.run)
        
        # Connect worker's finished signal to thread's quit method
        worker.task_completed.connect(self.thread.quit)
        
        # Start the thread
        self.thread.start()
    
    def cleanup(self):
        """
        Clean up thread resources.
        Should be called when the thread is no longer needed.
        """
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        
        self.thread = None
    
    def __del__(self):
        """Ensure thread is cleaned up when manager is destroyed."""
        self.cleanup()
