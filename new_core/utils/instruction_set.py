"""
Instruction Set

This module provides functionality for managing instruction sets
used in speech-to-text and LLM processing.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class InstructionSet:
    """
    A set of custom vocabulary, instructions, language, model, and LLM settings for processing.
    
    This class represents a named collection of settings that can be applied
    to a processing request, including custom vocabulary, system instructions,
    preferred language, transcription model, and LLM processing options.
    
    The class also includes a hotkey setting that allows users to quickly switch
    between instruction sets using keyboard shortcuts.
    """
    name: str
    stt_vocabulary: str = ""
    stt_instructions: str = ""
    stt_language: Optional[str] = None  # Language code (e.g., "en", "ja"), None for auto-detection
    stt_model: str = "gpt-4o-transcribe"
    
    # LLM settings
    llm_enabled: bool = False
    llm_model: str = "gpt-4o"
    llm_instructions: str = ""
    llm_clipboard_text_enabled: bool = False
    llm_clipboard_image_enabled: bool = False
    
    # Hotkey setting
    hotkey: str = ""  # Hotkey string (e.g., "ctrl+shift+1", "alt+f1")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InstructionSet':
        """
        Create an InstructionSet instance from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing instruction set data.
            
        Returns
        -------
        InstructionSet
            A new InstructionSet instance.
        """
        return cls(
            name=data.get("name", ""),
            stt_vocabulary=data.get("stt_vocabulary", ""),
            stt_instructions=data.get("stt_instructions", ""),
            stt_language=data.get("stt_language", None),
            stt_model=data.get("stt_model", "gpt-4o-transcribe"),
            llm_enabled=data.get("llm_enabled", False),
            llm_model=data.get("llm_model", "gpt-4o"),
            llm_instructions=data.get("llm_instructions", ""),
            llm_clipboard_text_enabled=data.get("llm_clipboard_text_enabled", False),
            llm_clipboard_image_enabled=data.get("llm_clipboard_image_enabled", False),
            hotkey=data.get("hotkey", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this InstructionSet instance to a dictionary.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary representation of this instruction set.
        """
        return {
            "name": self.name,
            "stt_vocabulary": self.stt_vocabulary,
            "stt_instructions": self.stt_instructions,
            "stt_language": self.stt_language,
            "stt_model": self.stt_model,
            "llm_enabled": self.llm_enabled,
            "llm_model": self.llm_model,
            "llm_instructions": self.llm_instructions,
            "llm_clipboard_text_enabled": self.llm_clipboard_text_enabled,
            "llm_clipboard_image_enabled": self.llm_clipboard_image_enabled,
            "hotkey": self.hotkey
        }
    
    def update(self, stt_vocabulary: Optional[str] = None, stt_instructions: Optional[str] = None,
              stt_language: Optional[str] = None, stt_model: Optional[str] = None,
              llm_enabled: Optional[bool] = None, llm_model: Optional[str] = None,
              llm_instructions: Optional[str] = None, llm_clipboard_text_enabled: Optional[bool] = None,
              llm_clipboard_image_enabled: Optional[bool] = None, hotkey: Optional[str] = None) -> None:
        """
        Update this instruction set with new values.
        
        Parameters
        ----------
        stt_vocabulary : str, optional
            New vocabulary string, by default None (unchanged).
        stt_instructions : str, optional
            New instructions string, by default None (unchanged).
        stt_language : Optional[str], optional
            Language code (e.g., "en", "ja"), by default None (unchanged).
        stt_model : str, optional
            STT model ID to use, by default None (unchanged).
        llm_enabled : bool, optional
            Whether LLM processing is enabled, by default None (unchanged).
        llm_model : str, optional
            LLM model ID to use, by default None (unchanged).
        llm_instructions : str, optional
            LLM system instructions, by default None (unchanged).
        llm_clipboard_text_enabled : bool, optional
            Whether to include clipboard text in LLM input, by default None (unchanged).
        llm_clipboard_image_enabled : bool, optional
            Whether to include clipboard images in LLM input, by default None (unchanged).
        hotkey : str, optional
            Hotkey string for quick activation, by default None (unchanged).
        """
        if stt_vocabulary is not None:
            self.stt_vocabulary = stt_vocabulary
        
        if stt_instructions is not None:
            self.stt_instructions = stt_instructions
            
        if stt_language is not None:
            self.stt_language = stt_language
            
        if stt_model is not None:
            self.stt_model = stt_model
            
        if llm_enabled is not None:
            self.llm_enabled = llm_enabled
            
        if llm_model is not None:
            self.llm_model = llm_model
            
        if llm_instructions is not None:
            self.llm_instructions = llm_instructions
            
        if llm_clipboard_text_enabled is not None:
            self.llm_clipboard_text_enabled = llm_clipboard_text_enabled
            
        if llm_clipboard_image_enabled is not None:
            self.llm_clipboard_image_enabled = llm_clipboard_image_enabled
            
        if hotkey is not None:
            self.hotkey = hotkey