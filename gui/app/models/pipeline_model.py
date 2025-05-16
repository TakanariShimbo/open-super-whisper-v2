"""
Pipeline Model

This module provides the model component for managing the transcription pipeline
in the Super Whisper application.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QThread

from core.pipelines.pipeline import Pipeline
from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet


class ProcessingThread(QThread):
    """
    Thread for processing audio files asynchronously.

    This class is used to process audio files asynchronously.
    It is used to handle the processing of audio files in the pipeline.

    Attributes
    ----------
    completed: pyqtSignal
        Signal for handling completion of processing
    failed: pyqtSignal
        Signal for handling failure of processing
    progress: pyqtSignal
        Signal for handling streaming progress updates
    """
    
    completed = pyqtSignal(object)
    failed = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(
        self, 
        pipeline: Pipeline, 
        audio_file_path: str, 
        language: str | None = None, 
        clipboard_text: str | None = None, 
        clipboard_image: bytes | None = None
    ) -> None:
        """
        Initialize with processing parameters.
        
        Parameters
        ----------
        pipeline: Pipeline
            The pipeline to use for processing
        audio_file_path: str
            The path to the audio file to process
        language: str | None
            The language to use for processing
        """
        super().__init__()
        self.pipeline = pipeline
        self.audio_file_path = audio_file_path
        self.language = language
        self.clipboard_text = clipboard_text
        self.clipboard_image = clipboard_image
        
    def run(self) -> None:
        """
        Execute the processing task.
        """
        try:
            # Process the audio file with streaming updates
            result = self.pipeline.process(
                self.audio_file_path,
                self.language,
                self.clipboard_text,
                self.clipboard_image,
                stream_callback=self.progress.emit
            )
            self.completed.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class PipelineModel(QObject):
    """
    Model for handling the speech-to-text transcription pipeline.

    This class manages the pipeline for speech-to-text transcription,
    including initialization, processing, and state management.

    Attributes
    ----------
    processing_error: pyqtSignal
        Signal for handling processing errors
    processing_started: pyqtSignal
        Signal for handling processing start
    processing_complete: pyqtSignal
        Signal for handling processing completion
    processing_cancelled: pyqtSignal
        Signal for handling processing cancellation
    processing_state_changed: pyqtSignal
        Signal for handling processing state changes
    llm_stream_chunk: pyqtSignal
        Signal for handling LLM stream chunks
    """
    
    # Define signals
    processing_error = pyqtSignal(str)
    processing_started = pyqtSignal()
    processing_complete = pyqtSignal(PipelineResult)
    processing_cancelled = pyqtSignal()
    processing_state_changed = pyqtSignal(bool)
    llm_stream_chunk = pyqtSignal(str)
    
    def __init__(self, api_key: str):
        """
        Initialize the pipeline model.

        Parameters
        ----------
        api_key: str
            The API key to use for the pipeline
        """
        super().__init__()

        self._pipeline = Pipeline(api_key=api_key)
        self._is_processing = False
        self._worker = None
    
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
            True if audio processing is in progress, False otherwise
        """
        return self._is_processing
    
    def reinitialize(self, api_key: str) -> None:
        """
        Reinitialize the pipeline with a new API key.
        """
        self._pipeline = Pipeline(api_key=api_key)
        
    def apply_instruction_set(self, instruction_set: InstructionSet) -> bool:
        """
        Apply an instruction set to the pipeline.

        Parameters
        ----------
        instruction_set: InstructionSet
            The instruction set to apply to the pipeline
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
            True if recording is started, False otherwise
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
        Stop recording audio and return the file path.

        Returns
        -------
        str | None
            The file path of the recorded audio, or None if an error occurs
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
        Process an audio file through the pipeline asynchronously.

        Parameters
        ----------
        audio_file_path: str
            The path to the audio file to process
        language: str | None
            The language to use for processing
        clipboard_text: str | None
            The text to use for processing
        clipboard_image: bytes | None
            The image to use for processing

        Returns
        -------
        bool
            True if processing is started, False otherwise
        """
        if not self._pipeline:
            self.processing_error.emit("Pipeline not initialized")
            return False
        
        if self._is_processing:
            self.processing_error.emit("Processing already in progress")
            return False
            
        try:
            # Update state
            self._is_processing = True
            self.processing_state_changed.emit(True)
            self.processing_started.emit()
            
            # Create and configure worker thread
            self._worker = ProcessingThread(
                self._pipeline,
                audio_file_path,
                language,
                clipboard_text,
                clipboard_image
            )
            
            # Connect signals
            self._worker.completed.connect(self._on_processing_completed)
            self._worker.failed.connect(self._on_processing_failed)
            self._worker.progress.connect(self.llm_stream_chunk)
            
            # Start processing
            self._worker.start()
            return True
            
        except Exception as e:
            self._is_processing = False
            self.processing_state_changed.emit(False)
            self.processing_error.emit(f"Error processing audio: {str(e)}")
            return False
    
    def _on_processing_completed(self, result: PipelineResult) -> None:
        """
        Handle successful completion of processing.

        Parameters
        ----------
        result: PipelineResult
            The result of the processing
        """
        self._is_processing = False
        self.processing_state_changed.emit(False)
        
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
            
        self.processing_complete.emit(result)
    
    def _on_processing_failed(self, error: str) -> None:
        """
        Handle processing failure.

        Parameters
        ----------
        error: str
            The error message
        """
        self._is_processing = False
        self.processing_state_changed.emit(False)
        
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
            
        self.processing_error.emit(f"Processing failed: {error}")
    
    def cancel_processing(self) -> bool:
        """
        Cancel the current processing task if one is running.

        Returns
        -------
        bool
            True if processing is cancelled, False otherwise
        """
        if not self._is_processing or not self._worker:
            return False
        
        # Terminate and clean up
        self._worker.terminate()
        self._worker.wait(1000)
        self._worker.deleteLater()
        self._worker = None
        
        # Update state
        self._is_processing = False
        self.processing_state_changed.emit(False)
        self.processing_cancelled.emit()
        
        return True
