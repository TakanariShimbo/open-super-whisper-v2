"""
Recorder Model

This module provides a model class that interfaces with the core AudioRecorder.
It adapts the core functionality to fit into the MVC architecture.
"""
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

# Import the core audio recorder
from core.recorder.audio_recorder import AudioRecorder

class RecorderModel(QObject):
    """
    Model class that interfaces with the AudioRecorder.
    
    This class provides a bridge between the core AudioRecorder functionality 
    and the application's controller. It wraps the AudioRecorder methods and
    emits signals when the recording state changes.
    
    Attributes
    ----------
    recording_started : pyqtSignal
        Signal emitted when recording starts
    recording_stopped : pyqtSignal
        Signal emitted when recording stops
    recording_error : pyqtSignal
        Signal emitted when a recording error occurs
    """
    # Define signals for communication
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal(str)  # Emits the file path of the recording
    recording_error = pyqtSignal(str)    # Emits error message
    
    def __init__(self) -> None:
        """
        Initialize the RecorderModel.
        
        Creates an instance of the core AudioRecorder and sets up the model.
        """
        super().__init__()
        
        # Create the core audio recorder
        self._recorder = AudioRecorder()
        
    @property
    def is_recording(self) -> bool:
        """
        Check if recording is in progress.
        
        Returns
        -------
        bool
            True if recording is in progress, False otherwise
        """
        return self._recorder.is_recording
    
    def start_recording(self) -> None:
        """
        Start recording audio.
        
        This method starts the audio recording and emits a signal when
        recording has started successfully.
        
        Raises
        ------
        RuntimeError
            If recording is already in progress or if there's an error starting the recording
        """
        try:
            if not self._recorder.is_recording:
                self._recorder.start_recording()
                self.recording_started.emit()
        except Exception as e:
            error_message = f"Error starting recording: {str(e)}"
            self.recording_error.emit(error_message)
            raise RuntimeError(error_message)
    
    def stop_recording(self) -> None:
        """
        Stop recording audio.
        
        This method stops the audio recording and emits a signal with
        the path to the recorded file when recording has stopped successfully.
        
        If not recording, this method does nothing.
        """
        if self._recorder.is_recording:
            try:
                file_path = self._recorder.stop_recording()
                if file_path:
                    self.recording_stopped.emit(file_path)
                else:
                    self.recording_error.emit("Recording failed to save")
            except Exception as e:
                error_message = f"Error stopping recording: {str(e)}"
                self.recording_error.emit(error_message)
