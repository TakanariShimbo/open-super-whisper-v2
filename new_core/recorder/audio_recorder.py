"""
Audio Recorder Module

This module provides implementation for recording audio from the microphone.

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
import threading
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
from datetime import datetime
from typing import Optional, List, Dict, Any


class MicrophoneError(Exception):
    """
    Base class for microphone-related errors.
    
    This is the parent exception for all microphone-related issues.
    Use the more specific child exceptions when possible to provide
    clearer error information.
    """
    pass


class NoMicrophoneError(MicrophoneError):
    """
    Exception raised when no microphone is available.
    
    This error occurs when the system cannot detect any input audio devices.
    Troubleshooting:
    - Check if a microphone is connected to your computer
    - Verify the microphone is not disabled in your system settings
    - Try connecting a different microphone
    """
    pass


class MicrophoneAccessError(MicrophoneError):
    """
    Exception raised when microphone exists but cannot be accessed.
    
    This error occurs when a microphone is detected but cannot be used
    for recording due to permission issues or hardware problems.
    
    Troubleshooting:
    - Check application permissions to access the microphone
    - Verify no other application is currently using the microphone
    - Check if the microphone drivers are properly installed
    - Try restarting your computer
    """
    pass


class AudioRecorder:
    """
    Implementation for recording audio from the microphone.
    
    This class provides methods to start and stop recording audio from the
    default microphone, with implementation using sounddevice and soundfile.
    It manages the audio recording process in a separate thread and handles
    common recording errors.
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
            
        Notes
        -----
        This method queries all audio devices and checks for those
        that support audio input (have input channels).
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
    def get_available_microphones() -> List[Dict[str, Any]]:
        """
        Get all available microphone devices on the system.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of microphone devices with their details including:
            - name: device name
            - hostapi: host API index
            - max_input_channels: number of input channels
            - max_output_channels: number of output channels
            - default_samplerate: default sample rate
            
        Notes
        -----
        If no microphones are found or an error occurs, an empty list is returned.
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
    
    def is_recording_active(self) -> bool:
        """
        Check if audio is currently being recorded.
        
        Returns
        -------
        bool
            True if recording is in progress, False otherwise.
            
        Notes
        -----
        This is a real-time status check that can be called at any time
        to determine if a recording session is active.
        """
        return self._recording_in_progress
    
    def start_recording(self) -> None:
        """
        Start recording audio from the microphone.
        
        This method will start recording audio in a separate thread and
        set the internal recording flag to True.
        
        Raises
        ------
        NoMicrophoneError
            If no microphone is available on the system.
            Troubleshooting: Connect a microphone and try again.
            
        MicrophoneAccessError
            If microphone exists but cannot be accessed due to permission
            issues or if it's being used by another application.
            Troubleshooting: Check microphone permissions and ensure no
            other application is using it.
            
        Notes
        -----
        The recording continues until stop_recording() is called.
        Audio data is stored in memory and written to a file when
        stop_recording() is called.
        """
        # Check if any microphone is available
        if not self.check_microphone_availability():
            raise NoMicrophoneError(
                "No microphone detected. Please connect a microphone and try again. "
                "If a microphone is already connected, check if it's properly "
                "recognized by your operating system."
            )
        
        # Reset audio data
        self.recorded_audio_frames = []
        
        # Create a unique temporary file for this recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_recording_path = os.path.join(
            self._temporary_directory, f"whisper_recording_{timestamp}.wav"
        )
        
        # Set recording flag
        self._recording_in_progress = True
        
        try:
            # Start recording in a separate thread
            self._recording_thread = threading.Thread(target=self._recording_process)
            self._recording_thread.daemon = True
            self._recording_thread.start()
            
            print(f"Started recording to {self._current_recording_path}")
        except Exception as e:
            self._recording_in_progress = False
            error_msg = (
                f"Failed to start recording: {str(e)}. "
                "Check if your microphone is properly connected and not being used "
                "by another application. You may need to restart your computer "
                "if the problem persists."
            )
            print(error_msg)
            raise MicrophoneAccessError(error_msg)
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording audio and return the path to the recorded file.
        
        Returns
        -------
        Optional[str]
            Path to the recorded audio file, or None if recording failed
            or no recording was in progress.
            
        Notes
        -----
        This method stops the active recording, saves the recorded audio
        to a WAV file, and returns the path to that file for further
        processing (e.g., transcription).
        
        If no audio data was recorded or an error occurs during saving,
        None is returned.
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
            try:
                # Concatenate all audio chunks
                audio_data = np.concatenate(self.recorded_audio_frames, axis=0)
                
                # Save to WAV file
                sf.write(self._current_recording_path, audio_data, self.sample_rate)
                print(f"Stopped recording to {self._current_recording_path}")
                
                # Return the path to the recorded file
                return self._current_recording_path
            except Exception as e:
                print(f"Error saving audio file: {e}. The recording may be corrupted or incomplete.")
                return None
        else:
            print("No audio data recorded. The recording may have been too short or the microphone was muted.")
            return None
    
    def _recording_process(self) -> None:
        """
        Internal method to record audio data from the microphone.
        
        This method is run in a separate thread and continuously
        records audio until the recording flag is set to False.
        
        Notes
        -----
        This method uses the sounddevice library to capture audio frames
        and stores them in the recorded_audio_frames list. It includes
        error handling for common recording issues.
        
        The audio data is collected in chunks to avoid excessive memory usage.
        """
        try:
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
                
                Notes
                -----
                This callback is called for each audio chunk and appends
                the data to the recorded_audio_frames list if recording
                is still active.
                """
                if status:
                    print(f"Recording status warning: {status}")
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
                    
        except sd.PortAudioError as e:
            error_msg = (
                f"Microphone access error: {e}. "
                "This may be caused by another application using the microphone, "
                "a disconnected microphone, or permission issues. "
                "Try closing other applications that might be using the microphone "
                "or reconnecting your microphone."
            )
            print(error_msg)
            self._recording_in_progress = False
            # No need to raise the exception here as this runs in a separate thread
            # The error handling should be done in the calling code
            
        except Exception as e:
            error_msg = (
                f"Recording error: {e}. "
                "This may be a hardware or system issue. "
                "Try restarting the application or checking your audio drivers."
            )
            print(error_msg)
            self._recording_in_progress = False
