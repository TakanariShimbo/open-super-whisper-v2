"""
Audio Recorder Module

This module provides implementation for recording audio from the microphone.
"""

# Standard library imports
import os
import tempfile
from datetime import datetime
from typing import Optional, List, Dict, Any

# Third-party imports
import numpy as np
import sounddevice as sd
import soundfile as sf


class AudioRecorder:
    """
    Implementation for recording audio from the microphone.
    
    This class provides methods to start and stop recording audio from the
    microphone, with implementation using sounddevice and soundfile.
    It uses a callback-based approach for recording without separate threads.
    
    Examples
    --------
    Basic usage:
    
    >>> recorder = AudioRecorder()
    >>> # Start recording audio
    >>> recorder.start_recording()
    >>> # Record for a few seconds...
    >>> # Stop recording and get the path to the saved file
    >>> file_path = recorder.stop_recording()
    >>> print(f"Recording saved to: {file_path}")
    
    Custom configuration:
    
    >>> # Create recorder with default settings
    >>> recorder = AudioRecorder()
    >>> # Set custom parameters before recording
    >>> recorder.set_recording_parameters(
    >>>     sample_rate=AudioRecorder.SAMPLE_RATES['high'],  # 44100 Hz
    >>>     channels=AudioRecorder.CHANNEL_MODES['stereo']   # 2 channels
    >>> )
    >>> # Set a different device
    >>> devices = AudioRecorder.get_available_microphones()
    >>> if len(devices) > 1:
    >>>     recorder.set_recording_device(devices[1]['index'])
    >>> # Start recording
    >>> recorder.start_recording()
    >>> # Later, stop recording
    >>> file_path = recorder.stop_recording()
    """
    
    # Class constants for commonly used settings
    CHANNEL_MODES: Dict[str, int] = {
        'mono': 1,
        'stereo': 2,
        'quad': 4
    }
    
    SAMPLE_RATES: Dict[str, int] = {
        'low': 8000,
        'standard': 16000,
        'medium': 22050,
        'high': 44100,
        'studio': 48000,
        'hd': 96000
    }
    
    def __init__(self) -> None:
        """
        Initialize the AudioRecorder with default settings.
        """
        # Internal state variables
        self._temporary_directory = tempfile.gettempdir()
        self._current_recording_path: Optional[str] = None
        self._audio_stream: Optional[sd.InputStream] = None
        self._device_id: Optional[int] = None
        
        # Recording parameters with default values
        self._sample_rate = self.SAMPLE_RATES['standard']  # 16000 Hz
        self._channels = self.CHANNEL_MODES['mono']        # 1 channel
        
        # Storage for recording data
        self._recorded_audio_frames: List[np.ndarray] = []
    
    @property
    def is_recording(self) -> bool:
        """
        Check if audio is currently being recorded.
        
        Returns
        -------
        bool
            True if recording is in progress, False otherwise.
        """
        return self._audio_stream is not None and self._audio_stream.active
        
    @property
    def current_recording_path(self) -> Optional[str]:
        """
        Get the path of the current or most recent recording.
        
        Returns
        -------
        Optional[str]
            Path to the recording file, or None if no recording has been made.
        """
        return self._current_recording_path
    
    @property
    def current_device(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently selected recording device.
        
        Returns
        -------
        Optional[Dict[str, Any]]
            Dictionary with device information, or None if using the default device.
        """
        if self._device_id is None:
            return None
        
        devices = self.get_available_microphones()
        for device in devices:
            if device.get('index') == self._device_id:
                return device
        
        return None
    
    @staticmethod
    def check_microphone_availability() -> bool:
        """
        Check if any microphone is available on the system.
        
        Returns
        -------
        bool
            True if at least one input device is available, False otherwise.
        """
        devices = sd.query_devices()
        
        # Check if there's at least one input device
        for device in devices:
            if device['max_input_channels'] > 0:
                return True
                
        # No input device found
        return False
            
    @staticmethod
    def get_available_microphones() -> List[Dict[str, Any]]:
        """
        Get all available microphone devices on the system.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of microphone devices with their details
        
        Examples
        --------
        >>> mics = AudioRecorder.get_available_microphones()
        >>> for mic in mics:
        >>>     print(f"{mic['index']}. {mic['name']} ({mic['max_input_channels']} channels)")
        """
        devices = sd.query_devices()
        
        # Filter for input devices
        input_devices = [
            device for device in devices 
            if device['max_input_channels'] > 0
        ]
            
        return input_devices
    
    def set_recording_parameters(self, sample_rate: int, channels: int) -> None:
        """
        Set new recording parameters.
        
        Parameters
        ----------
        sample_rate : int
            Sample rate for recording in Hertz
        channels : int
            Number of audio channels
            
        Returns
        -------
        None
        
        Raises
        ------
        RuntimeError
            If recording is currently in progress.
        ValueError
            If invalid parameters are provided.
        """
        # Check if recording is in progress
        if self.is_recording:
            raise RuntimeError("Cannot change recording parameters while recording is active.")
        
        # Validate parameters
        if sample_rate <= 0:
            raise ValueError(f"Invalid sample rate: {sample_rate}. Must be positive.")
        if channels <= 0:
            raise ValueError(f"Invalid channels: {channels}. Must be positive.")
        
        # Set new parameters
        self._sample_rate = sample_rate
        self._channels = channels
    
    def set_recording_device(self, device_id: Optional[int]) -> bool:
        """
        Set the device to use for recording.
        
        Parameters
        ----------
        device_id : Optional[int]
            Device ID to use for recording, or None to use the default device.
            
        Returns
        -------
        bool
            True if the device was set successfully, False otherwise.
            
        Raises
        ------
        RuntimeError
            If recording is currently in progress.
        """
        # Check if recording is in progress
        if self.is_recording:
            raise RuntimeError("Cannot change recording device while recording is active.")
        
        # If None is passed, use the default device
        if device_id is None:
            self._device_id = None
            return True
        
        # Validate device ID
        devices = self.get_available_microphones()
        device_indices = [device.get('index') for device in devices]
        
        if device_id not in device_indices:
            return False
        
        # Set device ID
        self._device_id = device_id
        return True
    
    def clear_recorded_data(self) -> None:
        """
        Clear any recorded audio data without saving.
        
        This method clears the internal buffer of recorded audio frames
        but does not affect any already saved recordings.
        
        Returns
        -------
        None
        
        Raises
        ------
        RuntimeError
            If recording is currently in progress.
        """
        # Check if recording is in progress
        if self.is_recording:
            raise RuntimeError("Cannot clear recorded data while recording is active.")
        
        # Clear the recorded frames
        self._recorded_audio_frames = []
    
    def start_recording(self) -> None:
        """
        Start recording audio from the microphone.
        
        This method will start recording audio using a callback-based approach
        and set the internal recording flag to True.
        
        Returns
        -------
        None
        
        Raises
        ------
        RuntimeError
            If recording is already in progress.
        """
        # Check if already recording
        if self.is_recording:
            raise RuntimeError("Recording is already in progress.")
        
        # Reset audio data
        self._recorded_audio_frames = []
        
        # Setup the recording path
        self._setup_recording_path()
        
        # Start recording using sounddevice with callback
        try:
            self._audio_stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                device=self._device_id,
                callback=self._audio_callback
            )
            self._audio_stream.start()
        except Exception as e:
            self._audio_stream = None
            raise RuntimeError(f"Failed to start recording: {str(e)}")
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording audio and return the path to the recorded file.
        
        Returns
        -------
        Optional[str]
            Path to the recorded audio file, or None if no recording was in progress
            or if saving the recording failed.
        """
        # Check if not recording
        if not self.is_recording:
            return None
        
        # Store current stream to close it
        stream = self._audio_stream
        self._audio_stream = None
        
        # Stop and close the audio stream
        if stream is not None:
            stream.stop()
            stream.close()
        
        # Save the recording
        return self._save_recording()
    
    def _audio_callback(self, indata: np.ndarray, frames: int, 
                      time_info: Dict[str, float], status: int) -> None:
        """
        Callback function for the InputStream.
        
        This private method is called by sounddevice for each audio chunk
        and appends the data to our recording buffer.
        
        Parameters
        ----------
        indata : np.ndarray
            The recorded audio data as a NumPy array
        frames : int
            Number of frames in this chunk
        time_info : Dict[str, float]
            Dictionary with timing information
        status : int
            Status flag indicating potential errors
        """
        # Only append data if we have an active stream
        if self._audio_stream is not None and self._audio_stream.active:
            self._recorded_audio_frames.append(indata.copy())
    
    def _setup_recording_path(self) -> None:
        """
        Set up the path for saving the recording.
        
        This private method creates a unique file path for the current recording
        in the system's temporary directory.
        """
        # Create a unique temporary file for this recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_recording_path = os.path.join(
            self._temporary_directory, f"recording_{timestamp}.wav"
        )
    
    def _save_recording(self) -> Optional[str]:
        """
        Save the recorded audio data to a file.
        
        This private method concatenates all recorded audio frames and
        saves them to the pre-defined file path.
        
        Returns
        -------
        Optional[str]
            Path to the saved audio file, or None if saving failed or
            no audio data was recorded.
        """
        # Check if we have any recorded frames
        if len(self._recorded_audio_frames) == 0:
            return None
        
        try:
            # Concatenate all audio chunks
            audio_data = np.concatenate(self._recorded_audio_frames, axis=0)
            
            # Save to WAV file
            sf.write(self._current_recording_path, audio_data, self._sample_rate)
            
            # Return the path to the recorded file
            return self._current_recording_path
        except Exception as e:
            print(f"Error saving recording: {str(e)}")
            return None
