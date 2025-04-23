"""
Audio Recorder Interface

This module provides an interface for recording audio from the microphone.
"""

import os
import tempfile
import time
from typing import Optional


class AudioRecorder:
    """
    Interface for recording audio from the microphone.
    
    This class provides methods to start and stop recording audio from the
    default microphone. The actual audio recording implementation will be
    added later, but the interface is defined here.
    """
    
    def __init__(self):
        """
        Initialize the AudioRecorder.
        """
        self._recording = False
        self._temp_dir = tempfile.gettempdir()
        self._current_recording_path = None
    
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
        
        This method will start recording audio and set the internal
        recording flag to True. The actual implementation will be
        added later.
        """
        # Create a unique temporary file for this recording
        timestamp = int(time.time())
        self._current_recording_path = os.path.join(
            self._temp_dir, f"whisper_recording_{timestamp}.wav"
        )
        
        # Set recording flag
        self._recording = True
        
        # Placeholder for actual recording implementation
        print(f"Started recording to {self._current_recording_path}")
    
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
        
        # Set recording flag
        self._recording = False
        
        # Placeholder for actual recording implementation
        print(f"Stopped recording to {self._current_recording_path}")
        
        # Return the path to the recorded file
        return self._current_recording_path
