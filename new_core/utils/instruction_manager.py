"""
Instruction Manager

This module provides functionality for managing instruction sets
used in speech-to-text and LLM processing.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


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
    stt_vocabulary: List[str] = field(default_factory=list)
    stt_instructions: List[str] = field(default_factory=list)
    stt_language: Optional[str] = None  # Language code (e.g., "en", "ja"), None for auto-detection
    stt_model: str = "gpt-4o-transcribe"  # Default model ID
    
    # LLM settings
    llm_enabled: bool = False
    llm_model: str = "gpt-4o"
    llm_instructions: List[str] = field(default_factory=list)
    llm_clipboard_text_enabled: bool = False  # Whether to include clipboard text in LLM input
    llm_clipboard_image_enabled: bool = False  # Whether to include clipboard images in LLM input
    
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
            stt_vocabulary=data.get("stt_vocabulary", []),
            stt_instructions=data.get("stt_instructions", []),
            stt_language=data.get("stt_language", None),
            stt_model=data.get("stt_model", "gpt-4o-transcribe"),
            llm_enabled=data.get("llm_enabled", False),
            llm_model=data.get("llm_model", "gpt-4o"),
            llm_instructions=data.get("llm_instructions", []),
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


class InstructionManager:
    """
    Manager for instruction sets.
    
    This class provides methods to create, edit, and manage
    instruction sets for speech-to-text and LLM processing.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the InstructionManager.
        
        Parameters
        ----------
        config_dir : Optional[str], optional
            Directory to store/load instruction sets, by default None (uses default location)
        """
        self.sets: Dict[str, InstructionSet] = {}
        self.active_set_name: Optional[str] = None
 
    def get_active_set(self) -> Optional[InstructionSet]:
        """
        Get the currently active instruction set.
        
        Returns
        -------
        Optional[InstructionSet]
            The active instruction set, or None if no set is active.
        """
        if not self.active_set_name or self.active_set_name not in self.sets:
            return None
        return self.sets[self.active_set_name]
    
    def create_set(self, name: str, stt_vocabulary: List[str] = None, stt_instructions: List[str] = None, 
                stt_language: Optional[str] = None, stt_model: str = "gpt-4o-transcribe",
                llm_enabled: bool = False, llm_model: str = "gpt-4o", 
                llm_instructions: List[str] = None, llm_clipboard_text_enabled: bool = False,
                llm_clipboard_image_enabled: bool = False, hotkey: str = "") -> bool:
        """
        Create a new instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set.
        stt_vocabulary : List[str], optional
            List of custom vocabulary words, by default None.
        stt_instructions : List[str], optional
            List of system instructions, by default None.
        stt_language : Optional[str], optional
            Language code (e.g., "en", "ja"), or None for auto-detection, by default None.
        stt_model : str, optional
            STT model ID to use, by default "gpt-4o-transcribe".
        llm_enabled : bool, optional
            Whether LLM processing is enabled, by default False.
        llm_model : str, optional
            LLM model ID to use, by default "gpt-4o".
        llm_instructions : List[str], optional
            List of LLM system instructions, by default None.
        llm_clipboard_text_enabled : bool, optional
            Whether to include clipboard text in LLM input, by default False.
        llm_clipboard_image_enabled : bool, optional
            Whether to include clipboard images in LLM input, by default False.
        hotkey : str, optional
            Hotkey string for quick activation, by default empty string.
            
        Returns
        -------
        bool
            True if set was created, False if name already exists.
        """
        if name in self.sets:
            return False
        
        self.sets[name] = InstructionSet(
            name=name,
            stt_vocabulary=stt_vocabulary or [],
            stt_instructions=stt_instructions or [],
            stt_language=stt_language,
            stt_model=stt_model,
            llm_enabled=llm_enabled,
            llm_model=llm_model,
            llm_instructions=llm_instructions or [],
            llm_clipboard_text_enabled=llm_clipboard_text_enabled,
            llm_clipboard_image_enabled=llm_clipboard_image_enabled,
            hotkey=hotkey
        )
        
        # If this is the first set, make it active
        if len(self.sets) == 1:
            self.active_set_name = name
        
        return True
    
    def update_set(self, name: str, stt_vocabulary: List[str] = None, stt_instructions: List[str] = None,
                 stt_language: Optional[str] = None, stt_model: Optional[str] = None,
                 llm_enabled: Optional[bool] = None, llm_model: Optional[str] = None,
                 llm_instructions: List[str] = None, llm_clipboard_text_enabled: Optional[bool] = None,
                 llm_clipboard_image_enabled: Optional[bool] = None, hotkey: Optional[str] = None) -> bool:
        """
        Update an existing instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to update.
        stt_vocabulary : List[str], optional
            New vocabulary list, by default None (unchanged).
        stt_instructions : List[str], optional
            New instructions list, by default None (unchanged).
        stt_language : Optional[str], optional
            Language code (e.g., "en", "ja"), by default None (unchanged).
        stt_model : str, optional
            STT model ID to use, by default None (unchanged).
        llm_enabled : bool, optional
            Whether LLM processing is enabled, by default None (unchanged).
        llm_model : str, optional
            LLM model ID to use, by default None (unchanged).
        llm_instructions : List[str], optional
            List of LLM system instructions, by default None (unchanged).
        llm_clipboard_text_enabled : bool, optional
            Whether to include clipboard text in LLM input, by default None (unchanged).
        llm_clipboard_image_enabled : bool, optional
            Whether to include clipboard images in LLM input, by default None (unchanged).
        hotkey : str, optional
            Hotkey string for quick activation, by default None (unchanged).
            
        Returns
        -------
        bool
            True if set was updated, False if name doesn't exist.
        """
        if name not in self.sets:
            return False
        
        if stt_vocabulary is not None:
            self.sets[name].stt_vocabulary = stt_vocabulary
        
        if stt_instructions is not None:
            self.sets[name].stt_instructions = stt_instructions
            
        if stt_language is not None:
            self.sets[name].stt_language = stt_language
            
        if stt_model is not None:
            self.sets[name].stt_model = stt_model
            
        if llm_enabled is not None:
            self.sets[name].llm_enabled = llm_enabled
            
        if llm_model is not None:
            self.sets[name].llm_model = llm_model
            
        if llm_instructions is not None:
            self.sets[name].llm_instructions = llm_instructions
            
        if llm_clipboard_text_enabled is not None:
            self.sets[name].llm_clipboard_text_enabled = llm_clipboard_text_enabled
            
        if llm_clipboard_image_enabled is not None:
            self.sets[name].llm_clipboard_image_enabled = llm_clipboard_image_enabled
            
        if hotkey is not None:
            self.sets[name].hotkey = hotkey
        
        return True
    
    def delete_set(self, name: str) -> bool:
        """
        Delete an instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to delete.
            
        Returns
        -------
        bool
            True if set was deleted, False if name doesn't exist or if it's the last set.
        """
        # Check if the set exists
        if name not in self.sets:
            return False
        
        # Don't allow deleting the last set
        if len(self.sets) <= 1:
            return False
        
        # If deleting the active set, select another one first
        # This ensures active_set is always valid after deletion
        if name == self.active_set_name:
            # Find a different set to make active
            new_active_set_found = False
            for other_name in self.sets:
                if other_name != name:
                    self.active_set_name = other_name
                    new_active_set_found = True
                    break
            
            # Safety check - if we couldn't find a new active set, abort deletion
            if not new_active_set_found:
                return False
                
        # Now that active_set is handled safely, delete the set
        try:
            del self.sets[name]
            return True
        except KeyError:
            # Extra safety in case the key disappeared (this should never happen)
            return False
    
    def set_active(self, name: str) -> bool:
        """
        Set the active instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to make active.
            
        Returns
        -------
        bool
            True if set was made active, False if name doesn't exist.
        """
        if name not in self.sets:
            return False
        
        self.active_set_name = name
        return True
    
    def rename_set(self, old_name: str, new_name: str) -> bool:
        """
        Rename an instruction set.
        
        Parameters
        ----------
        old_name : str
            Current name of the instruction set.
        new_name : str
            New name for the instruction set.
            
        Returns
        -------
        bool
            True if set was renamed, False if old name doesn't
            exist or new name already exists.
        """
        if old_name not in self.sets or new_name in self.sets:
            return False
        
        # Create a new entry with the same contents but different name
        instruction_set = self.sets[old_name]
        self.sets[new_name] = InstructionSet(
            name=new_name,
            stt_vocabulary=instruction_set.stt_vocabulary,
            stt_instructions=instruction_set.stt_instructions,
            stt_language=instruction_set.stt_language,
            stt_model=instruction_set.stt_model,
            llm_enabled=instruction_set.llm_enabled,
            llm_model=instruction_set.llm_model,
            llm_instructions=instruction_set.llm_instructions,
            llm_clipboard_text_enabled=instruction_set.llm_clipboard_text_enabled,
            llm_clipboard_image_enabled=instruction_set.llm_clipboard_image_enabled,
            hotkey=instruction_set.hotkey
        )
        
        # Update active set name if needed
        if self.active_set_name == old_name:
            self.active_set_name = new_name
        
        # Remove old entry
        del self.sets[old_name]
        
        return True
    
    def get_all_sets(self) -> List[InstructionSet]:
        """
        Get all instruction sets.
        
        Returns
        -------
        List[InstructionSet]
            List of all instruction sets.
        """
        return list(self.sets.values())
    
    def get_active_stt_vocabulary(self) -> List[str]:
        """
        Get vocabulary from the active set.
        
        Returns
        -------
        List[str]
            List of vocabulary items from the active set,
            or an empty list if no active set.
        """
        active_set = self.get_active_set()
        if not active_set:
            return []
        return active_set.stt_vocabulary
    
    def get_active_stt_instructions(self) -> List[str]:
        """
        Get STT instructions from the active set.
        
        Returns
        -------
        List[str]
            List of STT instructions from the active set,
            or an empty list if no active set.
        """
        active_set = self.get_active_set()
        if not active_set:
            return []
        return active_set.stt_instructions
        
    def get_active_stt_language(self) -> Optional[str]:
        """
        Get language setting from the active set.
        
        Returns
        -------
        Optional[str]
            Language code from the active set,
            or None if no active set or no language specified.
        """
        active_set = self.get_active_set()
        if not active_set:
            return None
        return active_set.stt_language
        
    def get_active_stt_model(self) -> str:
        """
        Get STT model setting from the active set.
        
        Returns
        -------
        str
            STT model ID from the active set,
            or "gpt-4o-transcribe" if no active set.
        """
        active_set = self.get_active_set()
        if not active_set:
            return "gpt-4o-transcribe"
        return active_set.stt_model
    
    def get_active_llm_enabled(self) -> bool:
        """
        Get LLM enabled setting from the active set.
        
        Returns
        -------
        bool
            Whether LLM processing is enabled in the active set,
            or False if no active set.
        """
        active_set = self.get_active_set()
        if not active_set:
            return False
        return active_set.llm_enabled
    
    def get_active_llm_model(self) -> str:
        """
        Get LLM model setting from the active set.
        
        Returns
        -------
        str
            LLM model ID from the active set,
            or "gpt-4o" if no active set.
        """
        active_set = self.get_active_set()
        if not active_set:
            return "gpt-4o"
        return active_set.llm_model
    
    def get_active_llm_instructions(self) -> List[str]:
        """
        Get LLM instructions from the active set.
        
        Returns
        -------
        List[str]
            List of LLM instructions from the active set,
            or an empty list if no active set.
        """
        active_set = self.get_active_set()
        if not active_set:
            return []
        return active_set.llm_instructions
        
    def get_active_llm_clipboard_text_enabled(self) -> bool:
        """
        Get LLM clipboard text enabled setting from the active set.
        
        Returns
        -------
        bool
            Whether clipboard text should be included in LLM input in the active set,
            or False if no active set.
        """
        active_set = self.get_active_set()
        if not active_set:
            return False
        return active_set.llm_clipboard_text_enabled
        
    def get_active_llm_clipboard_image_enabled(self) -> bool:
        """
        Get LLM clipboard image enabled setting from the active set.
        
        Returns
        -------
        bool
            Whether clipboard images should be included in LLM input in the active set,
            or False if no active set.
        """
        active_set = self.get_active_set()
        if not active_set:
            return False
        return active_set.llm_clipboard_image_enabled
    
    def update_set_hotkey(self, name: str, hotkey: str) -> bool:
        """
        Update the hotkey for an instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set.
        hotkey : str
            Hotkey string.
            
        Returns
        -------
        bool
            True if set was updated, False if name doesn't exist.
        """
        if name not in self.sets:
            return False
        
        self.sets[name].hotkey = hotkey
        return True
    
    def find_set_by_hotkey(self, hotkey: str) -> Optional[InstructionSet]:
        """
        Find an instruction set by its hotkey.
        
        Parameters
        ----------
        hotkey : str
            Hotkey string.
            
        Returns
        -------
        Optional[InstructionSet]
            The instruction set with the given hotkey, or None if not found.
        """
        for instruction_set in self.sets.values():
            if instruction_set.hotkey == hotkey:
                return instruction_set
        return None
    
    def import_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Import instruction sets from an external dictionary.
        
        This method loads instruction set configurations from external
        data (e.g., from a JSON file) into the current manager instance.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing serialized instruction sets.
        """
        # Validate input data
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
            
        # Clear existing sets
        self.sets.clear()
        
        # Import active set name
        self.active_set_name = data.get("active_set", "")
        
        # Import sets
        sets_data = data.get("sets", [])
        if not isinstance(sets_data, list):
            raise ValueError("The 'sets' field must be a list")
            
        for set_data in sets_data:
            if not isinstance(set_data, dict):
                continue  # Skip invalid entries
                
            name = set_data.get("name", "")
            if name:
                self.sets[name] = InstructionSet.from_dict(set_data)
    
        # If no sets were loaded and active_set_name is empty, create a default set
        if not self.sets:
            default_name = "Default"
            self.create_set(default_name)
            self.active_set_name = default_name
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export instruction sets to a dictionary for external serialization.
        
        This method prepares the current instruction set configuration
        for saving to external storage (e.g., JSON file).
        
        Returns
        -------
        Dict[str, Any]
            Dictionary containing serialized instruction sets.
        """
        sets_data = [instruction_set.to_dict() for instruction_set in self.sets.values()]
        
        return {
            "active_set": self.active_set_name or "",
            "sets": sets_data
        }