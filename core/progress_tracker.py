"""
Transcription Progress Tracker

This module provides functionality to track and manage the progress
of audio file transcription in memory during a single session.
"""

from typing import Dict, Any, Optional, List, Union

class TranscriptionProgressTracker:
    """
    Class to track and manage the progress of audio transcription in memory.
    All data is stored in memory only without any file operations.
    """
    
    def __init__(self):
        """
        Initialize the progress tracker with in-memory storage only.
        """
        self.progress_data = {
            "processed_chunks": {}
        }
    
    def save_chunk_result(self, chunk_path: str, transcription: str) -> None:
        """
        Save the result for a processed chunk.
        
        Parameters
        ----------
        chunk_path : str
            Path to the processed chunk
        transcription : str
            Transcription result for the chunk
        """
        self.progress_data["processed_chunks"][chunk_path] = transcription
    
    def is_chunk_processed(self, chunk_path: str) -> bool:
        """
        Check if a chunk has already been processed.
        
        Parameters
        ----------
        chunk_path : str
            Path to the chunk to check
            
        Returns
        -------
        bool
            True if the chunk has been processed, False otherwise
        """
        return chunk_path in self.progress_data["processed_chunks"]
    
    def get_chunk_result(self, chunk_path: str) -> Optional[str]:
        """
        Get the transcription result for a processed chunk.
        
        Parameters
        ----------
        chunk_path : str
            Path to the chunk
            
        Returns
        -------
        Optional[str]
            Transcription result for the chunk, or None if not processed
        """
        return self.progress_data["processed_chunks"].get(chunk_path)
    
    def get_all_results(self) -> Dict[str, str]:
        """
        Get all processed chunk results.
        
        Returns
        -------
        Dict[str, str]
            Dictionary mapping chunk paths to transcription results
        """
        return self.progress_data["processed_chunks"]
    
    def reset_progress(self) -> None:
        """
        Reset progress data, clearing all processed chunks.
        """
        self.progress_data = {
            "processed_chunks": {}
        }
