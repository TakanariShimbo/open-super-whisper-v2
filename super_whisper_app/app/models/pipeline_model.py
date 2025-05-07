"""
Pipeline Model

This module provides the model component for managing the transcription pipeline
in the Super Whisper application.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from core.pipelines.pipeline import Pipeline
from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet
from gui.thread_management.thread_manager import ThreadManager


class PipelineModel(QObject):
    """
    Model for handling the speech-to-text transcription pipeline.
    
    This class encapsulates the core Pipeline functionality and provides
    a Qt-friendly interface with signals for pipeline events.
    
    Attributes
    ----------
    processing_error : pyqtSignal
        Signal emitted when a processing error occurs
    processing_started : pyqtSignal
        Signal emitted when processing starts
    processing_complete : pyqtSignal
        Signal emitted when processing completes with results
    processing_cancelled : pyqtSignal
        Signal emitted when processing is cancelled
    processing_state_changed : pyqtSignal
        Signal emitted when processing state changes (bool: is_processing)
    """
    
    # Define signals
    processing_error = pyqtSignal(str)
    processing_started = pyqtSignal()
    processing_complete = pyqtSignal(PipelineResult)
    processing_cancelled = pyqtSignal()
    processing_state_changed = pyqtSignal(bool)  # is_processing
    
    def __init__(self, api_key: str = ""):
        """
        Initialize the PipelineModel.
        
        Parameters
        ----------
        api_key : str, optional
            The API key to use for the underlying pipeline, by default ""
        """
        super().__init__()
        
        # Initialize the pipeline with the given API key
        try:
            self._pipeline = Pipeline(api_key=api_key) if api_key else None
        except ValueError:
            self._pipeline = None
        
        # Initialize the thread manager
        self._thread_manager = ThreadManager()
        
        # Connect thread manager signals
        self._thread_manager.taskCompleted.connect(self._on_task_completed)
        self._thread_manager.taskFailed.connect(self._on_task_failed)
        
        # Processing state tracking
        self._is_processing = False
        self._current_task_id = None
            
    @property
    def is_initialized(self) -> bool:
        """
        Check if the pipeline is properly initialized.
        
        Returns
        -------
        bool
            True if the pipeline is initialized, False otherwise
        """
        return self._pipeline is not None
    
    @property
    def is_recording(self) -> bool:
        """
        Check if recording is in progress.
        
        Returns
        -------
        bool
            True if recording is in progress, False otherwise
        """
        return self._pipeline.is_recording if self._pipeline else False
    
    @property
    def is_processing(self) -> bool:
        """
        Check if audio processing is in progress.
        
        Returns
        -------
        bool
            True if processing is in progress, False otherwise
        """
        return self._is_processing
    
    def initialize_pipeline(self, api_key: str) -> bool:
        """
        Initialize or reinitialize the pipeline with a new API key.
        
        Parameters
        ----------
        api_key : str
            The API key to use for the pipeline
            
        Returns
        -------
        bool
            True if initialization was successful, False otherwise
        """
        try:
            self._pipeline = Pipeline(api_key=api_key)
            return True
        except ValueError:
            self._pipeline = None
            self.processing_error.emit("Invalid API key")
            return False
    
    def apply_instruction_set(self, instruction_set: InstructionSet) -> bool:
        """
        Apply an instruction set to the pipeline.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The instruction set to apply
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        if not self._pipeline:
            self.processing_error.emit("Pipeline not initialized")
            return False
            
        try:
            self._pipeline.apply_instruction_set(instruction_set)
            return True
        except Exception as e:
            self.processing_error.emit(f"Error applying instruction set: {str(e)}")
            return False
    
    def start_recording(self) -> bool:
        """
        Start recording audio.
        
        Returns
        -------
        bool
            True if recording started successfully, False otherwise
        """
        if not self._pipeline:
            self.processing_error.emit("Pipeline not initialized")
            return False
            
        try:
            self._pipeline.start_recording()
            return True
        except Exception as e:
            self.processing_error.emit(f"Error starting recording: {str(e)}")
            return False
    
    def stop_recording(self) -> str | None:
        """
        Stop recording audio.
        
        Returns
        -------
        str or None
            Path to the recorded audio file, or None if recording failed
        """
        if not self._pipeline or not self._pipeline.is_recording:
            return None
            
        try:
            return self._pipeline.stop_recording()
        except Exception as e:
            self.processing_error.emit(f"Error stopping recording: {str(e)}")
            return None
    
    def _process_audio_task(self, audio_file_path: str, language: str | None = None,
                           clipboard_text: str | None = None, clipboard_image: bytes | None = None) -> PipelineResult:
        """
        Task function to process audio in a worker thread.
        
        Parameters
        ----------
        audio_file_path : str
            Path to the audio file to process
        language : str | None, optional
            Language code for transcription, by default None
        clipboard_text : str | None, optional
            Text from clipboard to include in LLM context, by default None
        clipboard_image : bytes | None, optional
            Image data from clipboard to include in LLM context, by default None
            
        Returns
        -------
        PipelineResult
            The result of the processing
            
        Raises
        ------
        Exception
            If processing fails
        """
        # Define a streaming callback function (not used in this simplified version)
        def stream_callback(chunk):
            # Could use thread manager to update UI with streaming chunks
            self._thread_manager.run_in_main_thread(lambda: print(f"Stream chunk: {chunk[:20]}..."))
        
        # Process the audio file
        return self._pipeline.process(
            audio_file_path,
            language,
            clipboard_text,
            clipboard_image,
            stream_callback=stream_callback
        )
    
    def process_audio(self, audio_file_path: str, language: str | None = None,
                     clipboard_text: str | None = None, clipboard_image: bytes | None = None) -> bool:
        """
        Process an audio file through the pipeline asynchronously.
        
        Parameters
        ----------
        audio_file_path : str
            Path to the audio file to process
        language : str | None, optional
            Language code for transcription, by default None
        clipboard_text : str | None, optional
            Text from clipboard to include in LLM context, by default None
        clipboard_image : bytes | None, optional
            Image data from clipboard to include in LLM context, by default None
            
        Returns
        -------
        bool
            True if processing started successfully, False otherwise
        """
        if not self._pipeline:
            self.processing_error.emit("Pipeline not initialized")
            return False
        
        # Don't start a new processing task if one is already running
        if self._is_processing:
            self.processing_error.emit("Processing already in progress")
            return False
            
        try:
            # Signal that processing has started
            self._is_processing = True
            self.processing_state_changed.emit(True)
            self.processing_started.emit()
            
            # Run the processing task in a worker thread
            self._current_task_id = self._thread_manager.run_in_worker_thread(
                "audio_processing",
                self._process_audio_task,
                audio_file_path,
                language,
                clipboard_text,
                clipboard_image
            )
            
            return True
            
        except Exception as e:
            self._is_processing = False
            self.processing_state_changed.emit(False)
            self.processing_error.emit(f"Error processing audio: {str(e)}")
            return False
    
    def cancel_processing(self) -> bool:
        """
        Cancel the current processing task if one is running.
        
        Returns
        -------
        bool
            True if cancellation was initiated, False if no task to cancel
        """
        if not self._is_processing or not self._current_task_id:
            return False
        
        # Check if the task is still in the thread manager's task list
        if self._current_task_id in self._thread_manager._current_tasks:
            # Terminate the worker thread
            worker = self._thread_manager._current_tasks[self._current_task_id]
            worker.terminate()
            
            # Clean up
            worker.deleteLater()
            del self._thread_manager._current_tasks[self._current_task_id]
            
            # Update state
            self._is_processing = False
            self._current_task_id = None
            self.processing_state_changed.emit(False)
            
            # Emit cancellation signal
            self.processing_cancelled.emit()
            
            return True
        
        return False
    
    def _on_task_completed(self, task_id: str, result: PipelineResult) -> None:
        """
        Handle task completion.
        
        Parameters
        ----------
        task_id : str
            Task ID
        result : PipelineResult
            Processing result
        """
        if task_id == self._current_task_id:
            # Update state
            self._is_processing = False
            self._current_task_id = None
            self.processing_state_changed.emit(False)
            
            # Emit completion signal
            self.processing_complete.emit(result)
    
    def _on_task_failed(self, task_id: str, error: str) -> None:
        """
        Handle task failure.
        
        Parameters
        ----------
        task_id : str
            Task ID
        error : str
            Error message
        """
        if task_id == self._current_task_id:
            # Update state
            self._is_processing = False
            self._current_task_id = None
            self.processing_state_changed.emit(False)
            
            # Emit error signal
            self.processing_error.emit(f"Processing failed: {error}")
