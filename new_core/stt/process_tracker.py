"""
Process Tracker

This module provides functionality to track and manage the progress
of audio processing in memory during a single session.
"""

from typing import Dict, Optional, Any

class ProcessTracker:
    """
    Class to track and manage the progress of audio processing in memory.
    All data is stored in memory only without any file operations.
    This class handles tracking of audio files and their corresponding results.
    """
    
    def __init__(self):
        """
        Initialize the process tracker with in-memory storage only.
        
        Notes
        -----
        This initializes an empty dictionary structure to track processed items
        and their corresponding results.
        """
        self.process_data = {
            "processed_chunks": {}
        }
    
    def store_chunk_result(self, chunk_path: str, result: Any) -> None:
        """
        Store the result for a processed audio chunk.
        
        Parameters
        ----------
        chunk_path : str
            Path or identifier of the processed audio chunk
        result : Any
            Result or data associated with the chunk
            
        Returns
        -------
        None
            This method doesn't return any value
            
        Raises
        ------
        TypeError
            If chunk_path is not a string
        """
        if not isinstance(chunk_path, str):
            raise TypeError("chunk_path must be a string")
            
        self.process_data["processed_chunks"][chunk_path] = result
    
    def has_chunk_been_processed(self, chunk_path: str) -> bool:
        """
        Check if a specific audio chunk has already been processed.
        
        Parameters
        ----------
        chunk_path : str
            Path or identifier of the audio chunk to check
            
        Returns
        -------
        bool
            True if the chunk has been processed, False otherwise
            
        Raises
        ------
        TypeError
            If chunk_path is not a string
        """
        if not isinstance(chunk_path, str):
            raise TypeError("chunk_path must be a string")
            
        return chunk_path in self.process_data["processed_chunks"]
    
    def retrieve_chunk_result(self, chunk_path: str) -> Optional[Any]:
        """
        Retrieve the result for a processed audio chunk.
        
        Parameters
        ----------
        chunk_path : str
            Path or identifier of the audio chunk
            
        Returns
        -------
        Optional[Any]
            Result for the chunk, or None if not processed
            
        Raises
        ------
        TypeError
            If chunk_path is not a string
        """
        if not isinstance(chunk_path, str):
            raise TypeError("chunk_path must be a string")
            
        return self.process_data["processed_chunks"].get(chunk_path)
        
    def get_all_chunk_results(self) -> Dict[str, Any]:
        """
        Retrieve all processed chunks and their results.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary mapping chunk paths to their results
            
        Notes
        -----
        This method returns a copy of the internal data to prevent 
        accidental modification of the stored data.
        """
        return self.process_data["processed_chunks"].copy()
        
    def clear_all_progress_data(self) -> None:
        """
        Clear all stored progress data and reset the tracker.
        
        Returns
        -------
        None
            This method doesn't return any value
            
        Notes
        -----
        This operation cannot be undone and all tracked progress will be lost.
        """
        self.process_data = {
            "processed_chunks": {}
        }
