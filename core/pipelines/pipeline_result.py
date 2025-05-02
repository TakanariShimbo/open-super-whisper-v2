"""
Pipeline Result Model

This module provides a data container for pipeline processing results.
"""

# Standard library imports
from dataclasses import dataclass
from typing import Optional


@dataclass
class PipelineResult:
    """
    Container for pipeline processing results.
    
    This class holds the results of pipeline processing steps including
    transcription and optional LLM processing.
    
    Attributes
    ----------
    transcription : str
        The transcribed text.
    llm_response : Optional[str]
        The LLM response, if LLM processing was performed.
    llm_processed : bool
        Whether LLM processing was performed.
    """
    transcription: str
    llm_response: Optional[str] = None
    llm_processed: bool = False
    
    def get_combined_output(self) -> str:
        """
        Get a formatted output combining transcription and LLM response.
        
        Returns
        -------
        str
            Formatted output string.
        """
        if not self.llm_processed or not self.llm_response:
            return self.transcription
        
        return f"Transcription:\n{self.transcription}\n\nLLM Response:\n{self.llm_response}"
