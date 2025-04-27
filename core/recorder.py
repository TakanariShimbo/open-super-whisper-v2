"""
Audio Recorder Interface

This module provides real implementation for recording audio from the microphone.

The module includes error handling for cases when a microphone is not available or
cannot be accessed. These features ensure a better user experience by providing
clear error messages and preventing application crashes when audio recording
cannot be performed.

Error Handling Features:
- Detection of available microphones using sounddevice
- Custom exceptions for different microphone-related errors
- User-friendly error messages in the UI
- Prevention of recording attempts when no microphone is available
"""

import os
import time
import threading
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
from datetime import datetime
from typing import Optional, List, Dict, Any, Union


class MicrophoneError(Exception):
    """Base class for microphone-related errors."""
    pass


class NoMicrophoneError(MicrophoneError):
    """Exception raised when no microphone is available."""
    pass


class MicrophoneAccessError(MicrophoneError):
    """Exception raised when microphone exists but cannot be accessed."""
    pass


class AudioRecorder:
    """
    Implementation for recording audio from the microphone.
    
    This class provides methods to start and stop recording audio from the
    default microphone, with real implementation using sounddevice and soundfile.
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        Initialize the AudioRecorder.
        
        Parameters
        ----------
        sample_rate : int
            Sample rate for recording (Hz), by default 16000
        channels : int
            Number of audio channels, by default 1 (mono)
        """
        self._recording = False
        self._temp_dir = tempfile.gettempdir()
        self._current_recording_path = None
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_data = []
        self._record_thread = None
        
    @staticmethod
    def is_microphone_available() -> bool:
        """
        Check if any microphone is available.
        
        Returns
        -------
        bool
            True if at least one input device is available, False otherwise.
        """
        try:
            devices = sd.query_devices()
            
            # Check if there's at least one input device
            for device in devices:
                if device['max_input_channels'] > 0:
                    return True
                    
            # No input device found
            return False
            
        except Exception as e:
            print(f"Error checking microphone availability: {e}")
            return False
            
    @staticmethod
    def get_input_devices() -> List[Dict[str, Any]]:
        """
        Get all available input devices.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of input devices with their details.
        """
        try:
            devices = sd.query_devices()
            
            # Filter for input devices
            input_devices = [
                device for device in devices 
                if device['max_input_channels'] > 0
            ]
                
            return input_devices
            
        except Exception as e:
            print(f"Error getting input devices: {e}")
            return []
    
    def is_recording(self) -> bool:
        """
        Check if audio is currently being recorded.
        
        Returns
        -------
        bool
            True if recording is in progress, False otherwise.
        """
        return self._recording
    
    def start_recording(self) -> None:
        """
        Start recording audio from the microphone.
        
        This method will start recording audio in a separate thread and
        set the internal recording flag to True.
        
        Raises
        ------
        NoMicrophoneError
            If no microphone is available.
        MicrophoneAccessError
            If microphone exists but cannot be accessed.
        """
        # Check if any microphone is available
        if not self.is_microphone_available():
            raise NoMicrophoneError("No microphone detected. Please connect a microphone and try again.")
        
        # Reset audio data
        self.audio_data = []
        
        # Create a unique temporary file for this recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_recording_path = os.path.join(
            self._temp_dir, f"whisper_recording_{timestamp}.wav"
        )
        
        # Set recording flag
        self._recording = True
        
        try:
            # Start recording in a separate thread
            self._record_thread = threading.Thread(target=self._record)
            self._record_thread.daemon = True
            self._record_thread.start()
            
            print(f"Started recording to {self._current_recording_path}")
        except Exception as e:
            self._recording = False
            error_msg = f"Failed to start recording: {str(e)}"
            print(error_msg)
            raise MicrophoneAccessError(error_msg)
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording audio and return the path to the recorded file.
        
        Returns
        -------
        Optional[str]
            Path to the recorded audio file, or None if recording failed.
        """
        if not self._recording:
            return None
        
        # Set recording flag to False to stop the recording loop
        self._recording = False
        
        # Wait for the recording thread to finish
        if self._record_thread and self._record_thread.is_alive():
            self._record_thread.join()
        
        # Save the recorded audio data to file
        if len(self.audio_data) > 0:
            try:
                # Concatenate all audio chunks
                audio_data = np.concatenate(self.audio_data, axis=0)
                
                # Save to WAV file
                sf.write(self._current_recording_path, audio_data, self.sample_rate)
                print(f"Stopped recording to {self._current_recording_path}")
                
                # Return the path to the recorded file
                return self._current_recording_path
            except Exception as e:
                print(f"Error saving audio file: {e}")
                return None
        else:
            print("No audio data recorded")
            return None
    
    def _record(self) -> None:
        """
        Internal method to record audio data from the microphone.
        
        This method is run in a separate thread and continuously
        records audio until the recording flag is set to False.
        """
        try:
            def callback(indata, frames, time, status):
                """Callback function for the InputStream"""
                if status:
                    print(f"Status: {status}")
                if self._recording:
                    self.audio_data.append(indata.copy())
            
            # Start recording using sounddevice
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback
            ):
                # Continue until recording is stopped
                while self._recording:
                    sd.sleep(100)  # Sleep to prevent CPU overuse
                    
        except sd.PortAudioError as e:
            error_msg = f"Microphone access error: {e}"
            print(error_msg)
            self._recording = False
            # No need to raise the exception here as this runs in a separate thread
            # The error handling should be done in the calling code
            
        except Exception as e:
            error_msg = f"Recording error: {e}"
            print(error_msg)
            self._recording = False