"""
Instruction Set

This module provides functionality for managing instruction sets
used in speech-to-text and LLM processing.
"""

from dataclasses import dataclass
from typing import Any

from ..stt.stt_processor import STTProcessor
from ..llm.llm_processor import LLMProcessor


@dataclass
class InstructionSet:
    """
    A set of custom vocabulary, instructions, language, model, and LLM settings for processing.

    This class represents a named collection of settings that can be applied
    to a processing request, including custom vocabulary, system instructions,
    preferred language, transcription model, and LLM processing options.

    The class also includes a hotkey setting that allows users to quickly switch
    between instruction sets using keyboard shortcuts.

    Attributes
    ----------
    name : str
        Name of the instruction set.
    stt_vocabulary : str
        Custom vocabulary for speech-to-text, by default empty string.
    stt_instructions : str
        System instructions for speech-to-text, by default empty string.
    stt_language : Optional[str]
        Language code (e.g., "en", "ja"), None for auto-detection, by default None.
    stt_model : str
        Speech-to-text model ID, default from STTProcessor.
    llm_enabled : bool
        Whether LLM processing is enabled, by default False.
    llm_model : str
        LLM model ID to use, default from LLMProcessor.
    llm_instructions : str
        System instructions for LLM, by default empty string.
    llm_mcp_servers_json_str : str
        MCP servers JSON string, by default empty string.
    llm_web_search_enabled : bool
        Whether to enable web search in LLM, by default False.
    llm_clipboard_text_enabled : bool
        Whether to include clipboard text in LLM input, by default False.
    llm_clipboard_image_enabled : bool
        Whether to include clipboard images in LLM input, by default False.
    hotkey : str
        Hotkey string for quick activation (e.g., "ctrl+alt+1"), by default empty string.
    """

    name: str

    # STT settings
    stt_vocabulary: str = ""
    stt_instructions: str = ""
    stt_language: str = STTProcessor.DEFAULT_LANGUAGE_CODE
    stt_model: str = STTProcessor.DEFAULT_MODEL_ID

    # LLM settings
    llm_enabled: bool = False
    llm_model: str = LLMProcessor.DEFAULT_MODEL_ID
    llm_instructions: str = ""
    llm_mcp_servers_json_str: str = r"{}"
    llm_web_search_enabled: bool = False
    llm_clipboard_text_enabled: bool = False
    llm_clipboard_image_enabled: bool = False

    # Hotkey setting
    hotkey: str = ""  # Hotkey string (e.g., "ctrl+alt+1", "ctrl+alt+2")

    @classmethod
    def get_default(cls) -> "InstructionSet":
        """
        Get the default instruction set.

        Returns
        -------
        InstructionSet
            The default instruction set.
        """
        return cls(name="Default")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InstructionSet":
        """
        Create an InstructionSet instance from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary containing instruction set data.

        Returns
        -------
        InstructionSet
            A new InstructionSet instance.

        Raises
        ------
        ValueError
            If the name is not provided or is empty.
        """
        if data.get("name", "") == "":
            raise ValueError("Name is required")

        # Get default values
        default_set = cls.get_default()
        return cls(
            name=data.get("name"),
            stt_vocabulary=data.get("stt_vocabulary", default_set.stt_vocabulary),
            stt_instructions=data.get("stt_instructions", default_set.stt_instructions),
            stt_language=data.get("stt_language", default_set.stt_language),
            stt_model=data.get("stt_model", default_set.stt_model),
            llm_enabled=data.get("llm_enabled", default_set.llm_enabled),
            llm_model=data.get("llm_model", default_set.llm_model),
            llm_instructions=data.get("llm_instructions", default_set.llm_instructions),
            llm_mcp_servers_json_str=data.get("llm_mcp_servers_json_str", default_set.llm_mcp_servers_json_str),
            llm_web_search_enabled=data.get("llm_web_search_enabled", default_set.llm_web_search_enabled),
            llm_clipboard_text_enabled=data.get("llm_clipboard_text_enabled", default_set.llm_clipboard_text_enabled),
            llm_clipboard_image_enabled=data.get("llm_clipboard_image_enabled", default_set.llm_clipboard_image_enabled),
            hotkey=data.get("hotkey", default_set.hotkey),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this InstructionSet instance to a dictionary.

        Returns
        -------
        dict[str, Any]
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
            "llm_mcp_servers_json_str": self.llm_mcp_servers_json_str,
            "llm_web_search_enabled": self.llm_web_search_enabled,
            "llm_clipboard_text_enabled": self.llm_clipboard_text_enabled,
            "llm_clipboard_image_enabled": self.llm_clipboard_image_enabled,
            "hotkey": self.hotkey,
        }

    def update(
        self,
        stt_vocabulary: str | None = None,
        stt_instructions: str | None = None,
        stt_language: str | None = None,
        stt_model: str | None = None,
        llm_enabled: bool | None = None,
        llm_model: str | None = None,
        llm_instructions: str | None = None,
        llm_mcp_servers_json_str: str | None = None,
        llm_web_search_enabled: bool | None = None,
        llm_clipboard_text_enabled: bool | None = None,
        llm_clipboard_image_enabled: bool | None = None,
        hotkey: str | None = None,
    ) -> None:
        """
        Update this instruction set with new values.

        Parameters
        ----------
        stt_vocabulary : str, optional
            New vocabulary string, by default None (unchanged).
        stt_instructions : str, optional
            New instructions string, by default None (unchanged).
        stt_language : str | None, optional
            Language code (e.g., "en", "ja"), by default None (unchanged).
        stt_model : str, optional
            STT model ID to use, by default None (unchanged).
        llm_enabled : bool, optional
            Whether LLM processing is enabled, by default None (unchanged).
        llm_model : str, optional
            LLM model ID to use, by default None (unchanged).
        llm_instructions : str, optional
            LLM system instructions, by default None (unchanged).
        llm_mcp_servers_json_str : str, optional
            MCP servers JSON string, by default None (unchanged).
        llm_web_search_enabled : bool, optional
            Whether to enable web search in LLM, by default None (unchanged).
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

        if llm_mcp_servers_json_str is not None:
            self.llm_mcp_servers_json_str = llm_mcp_servers_json_str

        if llm_web_search_enabled is not None:
            self.llm_web_search_enabled = llm_web_search_enabled

        if llm_clipboard_text_enabled is not None:
            self.llm_clipboard_text_enabled = llm_clipboard_text_enabled

        if llm_clipboard_image_enabled is not None:
            self.llm_clipboard_image_enabled = llm_clipboard_image_enabled

        if hotkey is not None:
            self.hotkey = hotkey
