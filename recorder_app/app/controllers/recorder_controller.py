"""
Recorder Controller Module

This module contains the controller component for the recording application.
The RecorderController class manages the interaction between the UI and the models,
implementing the application's business logic.
"""
from typing import Optional, Dict
from PyQt6.QtCore import QObject, pyqtSignal

from ..models.recorder_model import RecorderModel
from ..models.hotkey_model import HotKeyModel

class RecorderController(QObject):
    """
    Controller class that manages the recording application logic.
    
    This class serves as a mediator between the user interface and models.
    It handles the recording and hotkey logic, and communicates
    with the UI through Qt signals.
    
    Attributes
    ----------
    recording_state_changed : pyqtSignal
        Signal emitted when recording state changes (with True for started, False for stopped)
    recording_file_saved : pyqtSignal
        Signal emitted when a recording is saved to a file
    error_occurred : pyqtSignal
        Signal emitted when an error occurs
    status_message : pyqtSignal
        Signal emitted to display status messages in the UI
    """
    # Signals to communicate with the UI
    recording_state_changed = pyqtSignal(bool)
    recording_file_saved = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    status_message = pyqtSignal(str)
    
    # Default hotkey for toggling recording
    DEFAULT_RECORDING_HOTKEY = "ctrl+shift+r"
    
    def __init__(self) -> None:
        """
        Initialize the RecorderController.
        
        Creates instances of the models and connects their signals to controller methods.
        """
        super().__init__()
        
        # Initialize models
        self._recorder_model = RecorderModel()
        self._hotkey_model = HotKeyModel()
        
        # Connect model signals to controller methods
        self._recorder_model.recording_started.connect(self._handle_recording_started)
        self._recorder_model.recording_stopped.connect(self._handle_recording_stopped)
        self._recorder_model.recording_error.connect(self._handle_recording_error)
        
        self._hotkey_model.hotkey_registered.connect(self._handle_hotkey_registered)
        self._hotkey_model.hotkey_error.connect(self._handle_hotkey_error)
        
        # Set up the default recording hotkey
        self._setup_default_hotkeys()
        
    def _setup_default_hotkeys(self) -> None:
        """
        Set up the default hotkey for recording.
        
        This private method registers the default hotkey for toggling recording.
        """
        self._hotkey_model.register_hotkey(
            self.DEFAULT_RECORDING_HOTKEY, 
            self.toggle_recording
        )
        
    def start_listening_for_hotkeys(self) -> None:
        """
        Start listening for hotkeys.
        
        This method activates the hotkey listener to begin responding to
        registered hotkeys.
        """
        try:
            self._hotkey_model.start_listening()
            self.status_message.emit("Hotkey listener started")
        except Exception as e:
            self.error_occurred.emit(f"Failed to start hotkey listener: {str(e)}")
    
    def stop_listening_for_hotkeys(self) -> None:
        """
        Stop listening for hotkeys.
        
        This method deactivates the hotkey listener.
        """
        if self._hotkey_model.stop_listening():
            self.status_message.emit("Hotkey listener stopped")
    
    def toggle_recording(self) -> None:
        """
        Toggle recording state.
        
        If recording is in progress, stops recording.
        If recording is not in progress, starts recording.
        """
        if self._recorder_model.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self) -> None:
        """
        Start recording audio.
        
        This method starts the audio recording process.
        """
        try:
            self._recorder_model.start_recording()
            # Model will emit signals that will be handled by our handlers
        except Exception as e:
            self.error_occurred.emit(f"Failed to start recording: {str(e)}")
    
    def stop_recording(self) -> None:
        """
        Stop recording audio.
        
        This method stops the audio recording process.
        """
        try:
            self._recorder_model.stop_recording()
            # Model will emit signals that will be handled by our handlers
        except Exception as e:
            self.error_occurred.emit(f"Failed to stop recording: {str(e)}")
    
    def _handle_recording_started(self) -> None:
        """
        Handle when recording starts.
        
        This private method is called when the recorder model emits a recording_started signal.
        """
        self.recording_state_changed.emit(True)
        self.status_message.emit("Recording started")
    
    def _handle_recording_stopped(self, file_path: str) -> None:
        """
        Handle when recording stops.
        
        This private method is called when the recorder model emits a recording_stopped signal.
        
        Parameters
        ----------
        file_path : str
            Path to the saved recording file
        """
        self.recording_state_changed.emit(False)
        self.recording_file_saved.emit(file_path)
        self.status_message.emit(f"Recording saved to: {file_path}")
    
    def _handle_recording_error(self, error_message: str) -> None:
        """
        Handle recording errors.
        
        This private method is called when the recorder model emits a recording_error signal.
        
        Parameters
        ----------
        error_message : str
            Error message from the recorder model
        """
        self.error_occurred.emit(f"Recording error: {error_message}")
    
    def _handle_hotkey_registered(self, hotkey_string: str) -> None:
        """
        Handle when a hotkey is registered.
        
        This private method is called when the hotkey model emits a hotkey_registered signal.
        
        Parameters
        ----------
        hotkey_string : str
            String representation of the registered hotkey
        """
        self.status_message.emit(f"Hotkey registered: {hotkey_string}")
    
    def _handle_hotkey_error(self, error_message: str) -> None:
        """
        Handle hotkey errors.
        
        This private method is called when the hotkey model emits a hotkey_error signal.
        
        Parameters
        ----------
        error_message : str
            Error message from the hotkey model
        """
        self.error_occurred.emit(f"Hotkey error: {error_message}")
