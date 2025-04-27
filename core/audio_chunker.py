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
from typing import List, Dict, Optional, Union

class AudioChunker:
    """
    Class for splitting audio files into smaller chunks.
    Used to handle the 25MB file size limitation of OpenAI's Whisper API.
    """
    
    def __init__(self, max_chunk_size_mb: float = 20.0, temp_dir: Optional[str] = None):
        """
        Initialize the AudioChunker.
        
        Parameters
        ----------
        max_chunk_size_mb : float, optional
            Maximum size of each chunk in MB, defaults to 20.0
        temp_dir : Optional[str], optional
            Directory to store temporary chunks, defaults to None (system temp directory)
        """
        self.max_chunk_size_mb = max_chunk_size_mb
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.chunk_dir = os.path.join(self.temp_dir, "whisper_chunks")
        
        # Create chunk directory if it doesn't exist
        os.makedirs(self.chunk_dir, exist_ok=True)
    
    def get_audio_duration(self, file_path: str) -> float:
        """
        Get the duration of an audio file in seconds.
        
        Parameters
        ----------
        file_path : str
            Path to the audio file
            
        Returns
        -------
        float
            Duration of the audio in seconds
        """
        try:
            probe = ffmpeg.probe(file_path)
            audio_stream = next((stream for stream in probe['streams'] 
                                if stream['codec_type'] == 'audio'), None)
            if audio_stream:
                return float(audio_stream['duration'])
            return 0.0
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0.0
    
    def split_audio_file(self, file_path: str) -> List[str]:
        """
        Split an audio file into chunks smaller than max_chunk_size_mb.
        
        Parameters
        ----------
        file_path : str
            Path to the audio file to split
            
        Returns
        -------
        List[str]
            List of paths to the generated chunks
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Get file size in MB
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # If file is already small enough, return it as is
        if file_size_mb <= self.max_chunk_size_mb:
            return [file_path]
        
        # Get audio duration
        total_duration = self.get_audio_duration(file_path)
        if total_duration <= 0:
            raise ValueError("Could not determine audio duration")
        
        # Calculate number of chunks needed
        num_chunks = math.ceil(file_size_mb / self.max_chunk_size_mb)
        
        # Add a safety margin by increasing the number of chunks
        num_chunks = int(num_chunks * 1.5)  # Add 50% more chunks for safety
        
        chunk_duration = total_duration / num_chunks
        
        chunks = []
        file_name = Path(file_path).stem
        
        for i in range(int(num_chunks)):
            start_time = i * chunk_duration
            chunk_path = os.path.join(self.chunk_dir, f"{file_name}_chunk_{i:03d}.wav")
            
            try:
                # Extract chunk using ffmpeg
                stream = ffmpeg.input(file_path, ss=start_time, t=chunk_duration)
                # Only reduce sample rate to 16kHz while preserving original channels
                stream = ffmpeg.output(stream, chunk_path, acodec='pcm_s16le', ar=16000)
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
                
                chunks.append(chunk_path)
            except Exception as e:
                print(f"Error splitting chunk {i+1}: {e}")
                # Continue with the next chunk even if this one fails
        
        return chunks
    
    def cleanup_chunks(self) -> None:
        """
        Clean up temporary chunk files.
        """
        if os.path.exists(self.chunk_dir):
            for file in os.listdir(self.chunk_dir):
                file_path = os.path.join(self.chunk_dir, file)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing file {file_path}: {e}")
