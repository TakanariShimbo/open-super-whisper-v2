"""
Audio Chunking Module

This module provides functionality to split large audio files into smaller chunks
to work around file size limitations for speech-to-text processing.
"""

import os
import tempfile
import math
from pathlib import Path

import ffmpeg


class AudioChunker:
    """
    Class for splitting audio files into smaller chunks.
    Used to handle file size limitations of speech-to-text processing APIs.
    
    This class provides methods to split audio files into smaller chunks,
    which can be useful when working with APIs that have file size limitations.
    It uses ffmpeg to perform the actual audio processing operations.
    
    Attributes
    ----------
    max_chunk_size_in_mb : float
        Maximum size for each audio chunk in megabytes.
    output_directory : str
        Directory to store temporary audio chunks.
    chunk_dir : str
        Full path to the directory containing audio chunks.
        
    Examples
    --------
    Basic usage:
    
    >>> chunker = AudioChunker()
    >>> # Split a large audio file into chunks
    >>> chunks = chunker.chunk_audio_file("large_recording.wav")
    >>> print(f"Split into {len(chunks)} chunks")
    Split into 5 chunks
    >>> # Process each chunk...
    >>> # Clean up temporary files when done
    >>> chunker.remove_temp_chunks()
    
    Custom configuration:
    
    >>> # Create chunker with smaller max chunk size (10MB)
    >>> chunker = AudioChunker(max_chunk_size_in_mb=10.0)
    >>> # Use a custom output directory
    >>> import os
    >>> custom_dir = os.path.join(os.path.expanduser("~"), "audio_processing")
    >>> chunker = AudioChunker(output_directory=custom_dir)
    >>> chunks = chunker.chunk_audio_file("large_recording.wav")
    """
    
    # Default settings for audio chunking
    DEFAULT_MAX_CHUNK_SIZE_MB: float = 20.0
    DEFAULT_SAMPLE_RATE: int = 16000
    DEFAULT_AUDIO_CODEC: str = 'pcm_s16le'
    
    def __init__(self, max_chunk_size_in_mb: float = DEFAULT_MAX_CHUNK_SIZE_MB, 
                 output_directory: str | None = None):
        """
        Initialize the AudioChunker.
        
        Parameters
        ----------
        max_chunk_size_in_mb : float, optional
            Maximum size of each chunk in MB, defaults to 20.0
        output_directory : str | None, optional
            Directory to store temporary chunks, defaults to None (system temp directory)
        """
        self._max_chunk_size_in_mb = max_chunk_size_in_mb
        self._output_directory = output_directory or tempfile.gettempdir()
        self._chunk_dir = os.path.join(self._output_directory, "audio_chunks")
        
        # Create chunk directory if it doesn't exist
        os.makedirs(self._chunk_dir, exist_ok=True)
    
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
        ValueError
            If the file doesn't contain an audio stream or can't be processed.
        """
        try:
            probe = ffmpeg.probe(audio_file_path)
            audio_stream = next((stream for stream in probe['streams'] 
                                if stream['codec_type'] == 'audio'), None)
            
            if not audio_stream:
                raise ValueError(f"No audio stream found in {audio_file_path}")
                
            return float(audio_stream['duration'])
        except ffmpeg.Error as e:
            raise ValueError(f"Error probing audio file: {str(e)}")
    
    def chunk_audio_file(self, audio_file_path: str) -> list[str]:
        """
        Chunk an audio file into smaller pieces smaller than max_chunk_size_in_mb.
        
        Parameters
        ----------
        audio_file_path : str
            Path to the audio file to chunk
            
        Returns
        -------
        list[str]
            List of paths to the generated chunks
            
        Raises
        ------
        FileNotFoundError
            If the audio file doesn't exist
        ValueError
            If the file can't be processed correctly
            
        Examples
        --------
        >>> chunker = AudioChunker()
        >>> chunks = chunker.chunk_audio_file("long_interview.wav")
        >>> print(f"Generated {len(chunks)} chunks")
        Generated 12 chunks
        """
        # Validate the file exists
        if not os.path.isfile(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
        # Get file size in MB
        file_size = os.path.getsize(audio_file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # If file is already small enough, return it as is
        if file_size_mb <= self._max_chunk_size_in_mb:
            return [audio_file_path]
        
        try:
            # Get audio duration
            total_duration = self._get_audio_duration(audio_file_path)
            
            # Calculate number of chunks needed
            num_chunks = math.ceil(file_size_mb / self._max_chunk_size_in_mb)
            
            # Add a safety margin by increasing the number of chunks
            num_chunks = int(num_chunks * 1.5)  # Add 50% more chunks for safety
            
            chunk_duration = total_duration / num_chunks
            
            chunk_file_paths = []
            file_name = Path(audio_file_path).stem
            
            for i in range(int(num_chunks)):
                start_time = i * chunk_duration
                chunk_path = os.path.join(self._chunk_dir, f"{file_name}_chunk_{i:03d}.wav")
                
                # Extract chunk using ffmpeg
                stream = ffmpeg.input(audio_file_path, ss=start_time, t=chunk_duration)
                # Only reduce sample rate to 16kHz while preserving original channels
                stream = ffmpeg.output(stream, chunk_path, 
                                     acodec=self.DEFAULT_AUDIO_CODEC, 
                                     ar=self.DEFAULT_SAMPLE_RATE)
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
                
                chunk_file_paths.append(chunk_path)
            
            return chunk_file_paths
        except Exception as e:
            raise ValueError(f"Error chunking audio file: {str(e)}")
        
    def remove_temp_chunks(self) -> int:
        """
        Remove temporary chunk files from disk.
        
        Returns
        -------
        int
            Number of files removed
        """
        removed_count = 0
        
        if os.path.exists(self._chunk_dir):
            # Remove individual files
            for file in os.listdir(self._chunk_dir):
                file_path = os.path.join(self._chunk_dir, file)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except OSError:
                        # Skip files that can't be removed
                        pass
            
            # Try to remove the directory itself
            try:
                os.rmdir(self._chunk_dir)
            except OSError:
                # Directory might not be empty, that's ok
                pass
                
        return removed_count
    
    @staticmethod
    def check_ffmpeg_available() -> bool:
        """
        Check if ffmpeg is installed and available.
        
        Returns
        -------
        bool
            True if ffmpeg is available, False otherwise
            
        Examples
        --------
        >>> if AudioChunker.check_ffmpeg_available():
        ...     chunker = AudioChunker()
        ...     # Proceed with audio processing
        ... else:
        ...     print("ffmpeg not available, audio chunking disabled")
        """
        try:
            # Try to run ffmpeg -version command
            result = ffmpeg.probe(None, cmd='ffmpeg', _ffmpeg_args=['-version'])
            return True
        except (ffmpeg.Error, FileNotFoundError):
            return False