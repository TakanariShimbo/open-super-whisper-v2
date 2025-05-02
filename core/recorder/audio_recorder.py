"""
Audio Recorder Module

This module provides implementation for recording audio from the microphone.
"""

# Standard library imports
import os
import threading
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
    default microphone, with implementation using sounddevice and soundfile.
    It manages the audio recording process in a separate thread.
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        """
        Initialize the AudioRecorder.
        
        Parameters
        ----------
        sample_rate : int
            Sample rate for recording in Hertz, by default 16000
        channels : int
            Number of audio channels, by default 1 (mono)
            
        Notes
        -----
        This initializes the recorder but does not start recording.
        Call start_recording() to begin capturing audio.
        """
        self._recording_in_progress = False
        self._temporary_directory = tempfile.gettempdir()
        self._current_recording_path: Optional[str] = None
        self.sample_rate = sample_rate
        self.channels = channels
        self.recorded_audio_frames: List[np.ndarray] = []
        self._recording_thread: Optional[threading.Thread] = None
        
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
        """
        devices = sd.query_devices()
        
        # Filter for input devices
        input_devices = [
            device for device in devices 
            if device['max_input_channels'] > 0
        ]
            
        return input_devices
    
    def is_recording_active(self) -> bool:
        """
        Check if audio is currently being recorded.
        
        Returns
        -------
        bool
            True if recording is in progress, False otherwise.
        """
        return self._recording_in_progress
    
    def start_recording(self) -> None:
        """
        Start recording audio from the microphone.
        
        This method will start recording audio in a separate thread and
        set the internal recording flag to True.
        """
        # Reset audio data
        self.recorded_audio_frames = []
        
        # Create a unique temporary file for this recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_recording_path = os.path.join(
            self._temporary_directory, f"whisper_recording_{timestamp}.wav"
        )
        
        # Set recording flag
        self._recording_in_progress = True
        
        # Start recording in a separate thread
        self._recording_thread = threading.Thread(target=self._recording_process)
        self._recording_thread.daemon = True
        self._recording_thread.start()
        
        print(f"Started recording to {self._current_recording_path}")
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording audio and return the path to the recorded file.
        
        Returns
        -------
        Optional[str]
            Path to the recorded audio file, or None if no recording was in progress.
        """
        if not self._recording_in_progress:
            return None
        
        # Set recording flag to False to stop the recording loop
        self._recording_in_progress = False
        
        # Wait for the recording thread to finish
        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.join()
        
        # Save the recorded audio data to file
        if len(self.recorded_audio_frames) > 0:
            # Concatenate all audio chunks
            audio_data = np.concatenate(self.recorded_audio_frames, axis=0)
            
            # Save to WAV file
            sf.write(self._current_recording_path, audio_data, self.sample_rate)
            print(f"Stopped recording to {self._current_recording_path}")
            
            # Return the path to the recorded file
            return self._current_recording_path
        else:
            print("No audio data recorded.")
            return None
    
    def _recording_process(self) -> None:
        """
        Internal method to record audio data from the microphone.
        
        This method is run in a separate thread and continuously
        records audio until the recording flag is set to False.
        """
        def callback(indata: np.ndarray, frames: int, time_info: Dict[str, float], status: int) -> None:
            """
            Callback function for the InputStream.
            
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
            if self._recording_in_progress:
                self.recorded_audio_frames.append(indata.copy())
        
        # Start recording using sounddevice
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback
        ):
            # Continue until recording is stopped
            while self._recording_in_progress:
                sd.sleep(100)  # Sleep to prevent CPU overuse
