"""
Transcription Progress Tracker

This module provides functionality to track and manage the progress
of audio file transcription, allowing for resumption of interrupted
transcription processes.
"""

import os
import json
from typing import Dict, Any, Optional, List, Union

class TranscriptionProgressTracker:
    """
    Class to track and manage the progress of audio transcription.
    Enables resumption of interrupted transcription processes.
    """
    
    def __init__(self, progress_file: str = "transcription_progress.json"):
        """
        Initialize the progress tracker.
        
        Parameters
        ----------
        progress_file : str, optional
            Path to the JSON file storing progress, default is "transcription_progress.json"
        """
        self.progress_file = progress_file
        self.progress_data = self._load_progress()
    
    def _load_progress(self) -> Dict[str, Any]:
        """
        Load progress data from file or initialize if file doesn't exist.
        
        Returns
        -------
        Dict[str, Any]
            Progress data dictionary
        """
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error loading progress file {self.progress_file}. File may be corrupted.")
            except Exception as e:
                print(f"Error loading progress file: {e}")
        
        # Default progress data structure
        return {
            "processed_chunks": {},
            "completed": False
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
        self._save_progress()
    
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
    
    def mark_completed(self) -> None:
        """
        Mark the transcription process as completed.
        """
        self.progress_data["completed"] = True
        self._save_progress()
    
    def is_completed(self) -> bool:
        """
        Check if the transcription process is completed.
        
        Returns
        -------
        bool
            True if the process is completed, False otherwise
        """
        return self.progress_data.get("completed", False)
    
    def _save_progress(self) -> None:
        """
        Save progress data to file.
        """
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def reset_progress(self) -> None:
        """
        Reset progress data, clearing all processed chunks and completion status.
        """
        self.progress_data = {
            "processed_chunks": {},
            "completed": False
        }
        self._save_progress()
