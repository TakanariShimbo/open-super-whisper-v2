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
    STT output and optional LLM processing.
    
    Attributes
    ----------
    stt_output : str
        The STT output.
    llm_output : Optional[str]
        The LLM output, if LLM processing was performed.
    is_llm_processed : bool
        Whether LLM processing was performed.
    """
    stt_output: str
    llm_output: Optional[str] = None
    is_llm_processed: bool = False
    
    def get_combined_output(self) -> str:
        """
        Get a formatted output combining STT output and LLM output.
        
        Returns
        -------
        str
            Formatted output string.
        """
        if not self.is_llm_processed or not self.llm_output:
            return self.stt_output
        
        return f"STT Output:\n{self.stt_output}\n\nLLM Output:\n{self.llm_output}"
