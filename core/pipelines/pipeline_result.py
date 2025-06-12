"""
Pipeline Result Model

This module provides a data container for pipeline processing results.
"""

from dataclasses import dataclass


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
    llm_output : str | None
        The LLM output, if LLM processing was performed.
    is_llm_processed : bool
        Whether LLM processing was performed.
    """

    stt_output: str
    llm_output: str | None = None
    is_llm_processed: bool = False
