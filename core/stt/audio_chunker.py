"""
Audio Chunking Module

This module provides functionality to split large audio files into smaller chunks
to work around file size limitations for speech-to-text processing.
"""

# Standard library imports
import os
import tempfile
import math
from pathlib import Path
from typing import List, Optional

# Third-party imports
import ffmpeg

class AudioChunker:
    """
    Class for splitting audio files into smaller chunks.
    Used to handle file size limitations of speech-to-text processing APIs.
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
        self.chunk_dir = os.path.join(self.output_directory, "audio_chunks")
        
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
        """
        probe = ffmpeg.probe(audio_file_path)
        audio_stream = next((stream for stream in probe['streams'] 
                            if stream['codec_type'] == 'audio'), None)
        
        return float(audio_stream['duration'])
    
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
        """
        # Get file size in MB
        file_size = os.path.getsize(audio_file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # If file is already small enough, return it as is
        if file_size_mb <= self.max_chunk_size_in_mb:
            return [audio_file_path]
        
        # Get audio duration
        total_duration = self._get_audio_duration(audio_file_path)
        
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
            
            # Extract chunk using ffmpeg
            stream = ffmpeg.input(audio_file_path, ss=start_time, t=chunk_duration)
            # Only reduce sample rate to 16kHz while preserving original channels
            stream = ffmpeg.output(stream, chunk_path, acodec='pcm_s16le', ar=16000)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            chunk_file_paths.append(chunk_path)
        
        return chunk_file_paths
    
    def remove_temp_chunks(self) -> None:
        """
        Remove temporary chunk files from disk.
        """
        if os.path.exists(self.chunk_dir):
            # Remove individual files
            for file in os.listdir(self.chunk_dir):
                file_path = os.path.join(self.chunk_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # Remove the directory itself
            os.rmdir(self.chunk_dir)