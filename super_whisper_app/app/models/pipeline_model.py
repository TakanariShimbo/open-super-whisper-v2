"""
Pipeline Model

This module provides the model component for managing the transcription pipeline
in the Super Whisper application.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from core.pipelines.pipeline import Pipeline
from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet

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
    """
    
    # Define signals
    processing_error = pyqtSignal(str)
    processing_started = pyqtSignal()
    processing_complete = pyqtSignal(PipelineResult)
    
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
    
    def process_audio(self, audio_file_path: str, language: str | None = None, 
                     clipboard_text: str | None = None, clipboard_image: bytes | None = None) -> bool:
        """
        Process an audio file through the pipeline.
        
        Parameters
        ----------
        audio_file_path : str
            Path to the audio file to process
        language : str, optional
            Language code for transcription, by default None
        clipboard_text : str, optional
            Text from clipboard to include in LLM context, by default None
        clipboard_image : bytes, optional
            Image data from clipboard to include in LLM context, by default None
            
        Returns
        -------
        bool
            True if processing started successfully, False otherwise
        """
        if not self._pipeline:
            self.processing_error.emit("Pipeline not initialized")
            return False
            
        try:
            # Signal that processing has started
            self.processing_started.emit()
            
            # Define a streaming callback function 
            # (not used in this simplified version)
            def stream_callback(chunk):
                # Could emit a chunk signal here if needed
                pass
            
            # Process the audio file
            result = self._pipeline.process(
                audio_file_path,
                language,
                clipboard_text,
                clipboard_image,
                stream_callback=stream_callback
            )
            
            # Signal that processing is complete
            self.processing_complete.emit(result)
            return True
            
        except Exception as e:
            self.processing_error.emit(f"Error processing audio: {str(e)}")
            return False
