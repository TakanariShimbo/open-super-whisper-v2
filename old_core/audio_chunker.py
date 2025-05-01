"""
Audio Chunking Module

This module provides functionality to split large audio files into smaller chunks
to work around the OpenAI Whisper API's 25MB file size limit.
"""

import os
import tempfile
import math
import ffmpeg
from pathlib import Path
from typing import List, Optional

class AudioChunkerError(Exception):
    """Base exception for all errors in the AudioChunker class."""
    pass

class AudioFileNotFoundError(AudioChunkerError):
    """Exception raised when the audio file does not exist."""
    pass

class AudioDurationError(AudioChunkerError):
    """Exception raised when the audio duration cannot be determined."""
    pass

class AudioChunkingError(AudioChunkerError):
    """Exception raised when there's an error during the chunking process."""
    pass

class AudioChunker:
    """
    Class for splitting audio files into smaller chunks.
    Used to handle the 25MB file size limitation of OpenAI's Whisper API.
    """
    
    def __init__(self, max_chunk_size_in_mb: float = 20.0, output_directory: Optional[str] = None):
        """
        Initialize the AudioChunker.
        
        Parameters
        ----------
        max_chunk_size_in_mb : float, optional
            Maximum size of each chunk in MB, defaults to 20.0
        output_directory : Optional[str], optional
            Directory to store temporary chunks, defaults to None (system temp directory)
        """
        self.max_chunk_size_in_mb = max_chunk_size_in_mb
        self.output_directory = output_directory or tempfile.gettempdir()
        self.chunk_dir = os.path.join(self.output_directory, "whisper_chunks")
        
        # Create chunk directory if it doesn't exist
        os.makedirs(self.chunk_dir, exist_ok=True)
    
    def _get_audio_duration(self, audio_file_path: str) -> float:
        """
        Get the duration of an audio file in seconds.
        
        Parameters
        ----------
        audio_file_path : str
            Path to the audio file
            
        Returns
        -------
        float
            Duration of the audio in seconds
            
        Raises
        ------
        AudioFileNotFoundError
            If the audio file does not exist
        AudioDurationError
            If the duration cannot be determined from the file
        """
        # Check if file exists before probing
        if not os.path.exists(audio_file_path):
            raise AudioFileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            probe = ffmpeg.probe(audio_file_path)
            audio_stream = next((stream for stream in probe['streams'] 
                                if stream['codec_type'] == 'audio'), None)
            if audio_stream and 'duration' in audio_stream:
                return float(audio_stream['duration'])
            
            # If no audio stream or no duration, raise a specific error
            raise AudioDurationError(f"Could not find audio duration in file: {audio_file_path}")
        except ffmpeg.Error as e:
            # Handle ffmpeg-specific errors
            error_message = f"FFmpeg error while probing audio file: {e.stderr.decode() if hasattr(e, 'stderr') else str(e)}"
            raise AudioDurationError(error_message) from e
        except Exception as e:
            # Handle all other unexpected errors
            raise AudioDurationError(f"Error getting audio duration: {str(e)}") from e
    
    def chunk_audio_file(self, audio_file_path: str) -> List[str]:
        """
        Chunk an audio file into smaller pieces smaller than max_chunk_size_in_mb.
        
        Parameters
        ----------
        audio_file_path : str
            Path to the audio file to chunk
            
        Returns
        -------
        List[str]
            List of paths to the generated chunks
            
        Raises
        ------
        AudioFileNotFoundError
            If the audio file does not exist
        AudioDurationError
            If the duration cannot be determined from the file
        AudioChunkingError
            If there's an error during the chunking process
        """
        # Check if file exists
        if not os.path.exists(audio_file_path):
            raise AudioFileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        # Get file size in MB
        try:
            file_size = os.path.getsize(audio_file_path)
            file_size_mb = file_size / (1024 * 1024)
        except OSError as e:
            raise AudioChunkingError(f"Failed to get file size: {str(e)}") from e
        
        # If file is already small enough, return it as is
        if file_size_mb <= self.max_chunk_size_in_mb:
            return [audio_file_path]
        
        # Get audio duration
        try:
            total_duration = self._get_audio_duration(audio_file_path)
            if total_duration <= 0:
                raise AudioDurationError(f"Invalid audio duration: {total_duration} seconds")
        except AudioDurationError as e:
            # Re-raise with more context
            raise AudioDurationError(f"Could not determine audio duration for chunking: {str(e)}") from e
        
        # Calculate number of chunks needed
        num_chunks = math.ceil(file_size_mb / self.max_chunk_size_in_mb)
        
        # Add a safety margin by increasing the number of chunks
        num_chunks = int(num_chunks * 1.5)  # Add 50% more chunks for safety
        
        chunk_duration = total_duration / num_chunks
        
        chunk_file_paths = []
        file_name = Path(audio_file_path).stem
        
        for i in range(int(num_chunks)):
            start_time = i * chunk_duration
            chunk_path = os.path.join(self.chunk_dir, f"{file_name}_chunk_{i:03d}.wav")
            
            try:
                # Extract chunk using ffmpeg
                stream = ffmpeg.input(audio_file_path, ss=start_time, t=chunk_duration)
                # Only reduce sample rate to 16kHz while preserving original channels
                stream = ffmpeg.output(stream, chunk_path, acodec='pcm_s16le', ar=16000)
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
                
                # Verify the chunk was created successfully
                if not os.path.exists(chunk_path) or os.path.getsize(chunk_path) == 0:
                    raise AudioChunkingError(f"Failed to create chunk {i+1}: Empty or missing file")
                
                chunk_file_paths.append(chunk_path)
            except ffmpeg.Error as e:
                error_message = f"FFmpeg error while chunking segment {i+1}: {e.stderr.decode() if hasattr(e, 'stderr') else str(e)}"
                raise AudioChunkingError(error_message) from e
            except Exception as e:
                raise AudioChunkingError(f"Error chunking segment {i+1}: {str(e)}") from e
        
        if not chunk_file_paths:
            raise AudioChunkingError("Failed to create any chunks from the audio file")
        
        return chunk_file_paths
    
    def remove_temp_chunks(self) -> None:
        """
        Remove temporary chunk files from disk.
        
        Raises
        ------
        OSError
            If there's an error removing the chunk files or directory
        """
        if os.path.exists(self.chunk_dir):
            try:
                # First attempt to remove individual files
                for file in os.listdir(self.chunk_dir):
                    file_path = os.path.join(self.chunk_dir, file)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                        except OSError as e:
                            print(f"Warning: Failed to remove file {file_path}: {str(e)}")
                
                # Then try to remove the directory itself
                try:
                    os.rmdir(self.chunk_dir)
                except OSError as e:
                    if os.listdir(self.chunk_dir):
                        print(f"Warning: Could not remove chunk directory as it still contains files: {str(e)}")
                    else:
                        print(f"Warning: Could not remove empty chunk directory: {str(e)}")
            except Exception as e:
                print(f"Warning: Error during chunk cleanup: {str(e)}")
