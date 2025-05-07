"""
Pipeline Worker Module

This module provides the PipelineWorker class for executing speech-to-text
processing tasks using the core pipeline in a separate thread.
"""

from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal

from core.pipelines.pipeline import Pipeline
from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet


class PipelineWorker(QObject):
    """
    Worker class for executing pipeline processing tasks.
    
    This class executes speech-to-text and optional LLM processing
    tasks using the core pipeline in a separate thread.
    
    Attributes
    ----------
    progress_updated : pyqtSignal
        Signal emitted when processing progress updates
    result_ready : pyqtSignal
        Signal emitted when processing produces a result
    stream_chunk : pyqtSignal
        Signal emitted when a streaming chunk is available
    processing_complete : pyqtSignal
        Signal emitted when processing is completed
    """
    
    # Signals
    progress_updated = pyqtSignal(int)
    result_ready = pyqtSignal(object)
    stream_chunk = pyqtSignal(str)
    processing_complete = pyqtSignal(PipelineResult)
    
    def __init__(self, pipeline: Pipeline) -> None:
        """
        Initialize the PipelineWorker.
        
        Parameters
        ----------
        pipeline : Pipeline
            The pipeline instance to use for processing
        """
        super().__init__()
        
        # Store pipeline
        self._pipeline = pipeline
        
        # Processing state
        self._abort_requested = False
        self._current_audio_file = None
        self._language = None
        self._clipboard_text = None
        self._clipboard_image = None
    
    def set_processing_parameters(self, audio_file: str, language: Optional[str] = None,
                              clipboard_text: Optional[str] = None, 
                              clipboard_image: Optional[bytes] = None) -> None:
        """
        Set the parameters for processing.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to process
        language : Optional[str], optional
            Language code for transcription, by default None
        clipboard_text : Optional[str], optional
            Text from clipboard to include in LLM input, by default None
        clipboard_image : Optional[bytes], optional
            Image data from clipboard to include in LLM input, by default None
        """
        self._current_audio_file = audio_file
        self._language = language
        self._clipboard_text = clipboard_text
        self._clipboard_image = clipboard_image
        self._abort_requested = False
    
    def start_task(self) -> None:
        """
        Start executing the processing task.
        
        This method is called when the thread is started.
        It processes the audio file using the pipeline and
        emits progress and result signals.
        """
        if not self._current_audio_file:
            self.result_ready.emit(Exception("No audio file specified"))
            self.processing_complete.emit(PipelineResult(transcription="No audio file specified"))
            return
        
        try:            
            # Create a callback for streaming LLM responses
            def stream_callback(chunk: str) -> None:
                self.stream_chunk.emit(chunk)
            
            # Process the audio file
            result = self._pipeline.process(
                self._current_audio_file,
                self._language,
                self._clipboard_text,
                self._clipboard_image,
                stream_callback=stream_callback
            )
            
            # Emit the result
            self.processing_complete.emit(result)
            
        except Exception as e:
            # Handle errors
            self.result_ready.emit(e)
            self.processing_complete.emit(PipelineResult(transcription=f"Error: {str(e)}"))
    
    def abort_current_task(self) -> None:
        """
        Abort the currently running task.
        
        Sets the abort flag so the task can check and abort if needed.
        """
        self._abort_requested = True
