"""
Instruction Manager

This module provides functionality for managing instruction sets
used in speech-to-text and LLM processing.
"""

import os
import json
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
    vocabulary: List[str] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    language: Optional[str] = None  # Language code (e.g., "en", "ja"), None for auto-detection
    model: str = "gpt-4o-transcribe"  # Default model ID
    
    # LLM settings
    llm_enabled: bool = False
    llm_model: str = "gpt-4o"
    llm_instructions: List[str] = field(default_factory=list)
    llm_clipboard_text_enabled: bool = False  # Whether to include clipboard text in LLM input
    llm_clipboard_image_enabled: bool = False  # Whether to include clipboard images in LLM input
    
    # Hotkey setting
    hotkey: str = ""  # Hotkey string (e.g., "ctrl+shift+1", "alt+f1")


class InstructionManager:
    """
    Manager for instruction sets.
    
    This class provides methods to create, load, save, and manage
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
        
        # Use provided config dir or default
        self.config_dir = config_dir or os.path.expanduser("~/.config/open-super-whisper")
        self.instruction_sets_file = os.path.join(self.config_dir, "instruction_sets.json")
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
    
    def load_instructions(self, instruction_set_name: Optional[str] = None) -> bool:
        """
        Load instruction sets from file.
        
        Parameters
        ----------
        instruction_set_name : Optional[str], optional
            Name of a specific instruction set to load, by default None (loads all)
            
        Returns
        -------
        bool
            True if instructions were loaded successfully, False otherwise.
        """
        try:
            # If instruction sets file doesn't exist, create default set
            if not os.path.exists(self.instruction_sets_file):
                # Create a default instruction set
                default_set = InstructionSet(
                    name="Default",
                    vocabulary=[],
                    instructions=[],
                    language=None,
                    model="gpt-4o-transcribe",
                    llm_enabled=False,
                    llm_model="gpt-4o",
                    llm_instructions=[],
                    llm_clipboard_text_enabled=False,
                    llm_clipboard_image_enabled=False,
                    hotkey=""
                )
                
                # Add to sets dictionary
                self.sets["Default"] = default_set
                self.active_set_name = "Default"
                
                # Save to file
                self.save_instructions()
                
                return True
            
            # Load instruction sets from file
            with open(self.instruction_sets_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Import the data
            self.import_from_dict(data)
            
            # If a specific set was requested, verify it was loaded
            if instruction_set_name and instruction_set_name not in self.sets:
                return False
                
            return True
            
        except Exception as e:
            print(f"Error loading instruction sets: {e}")
            return False
    
    def get_available_instruction_sets(self) -> List[str]:
        """
        Get all available instruction set names.
        
        Returns
        -------
        List[str]
            List of instruction set names.
        """
        return list(self.sets.keys())
    
    def save_instructions(self, instruction_set_name: Optional[str] = None) -> bool:
        """
        Save instruction sets to file.
        
        Parameters
        ----------
        instruction_set_name : Optional[str], optional
            Name of a specific instruction set to save, by default None (saves all)
            
        Returns
        -------
        bool
            True if instructions were saved successfully, False otherwise.
        """
        try:
            # If a specific set was specified but doesn't exist, return False
            if instruction_set_name and instruction_set_name not in self.sets:
                return False
            
            # Prepare data dict with all sets or just the specified one
            if instruction_set_name:
                # Only export the specified set
                sets_data = []
                instruction_set = self.sets[instruction_set_name]
                sets_data.append({
                    "name": instruction_set.name,
                    "vocabulary": instruction_set.vocabulary,
                    "instructions": instruction_set.instructions,
                    "language": instruction_set.language,
                    "model": instruction_set.model,
                    "llm_enabled": instruction_set.llm_enabled,
                    "llm_model": instruction_set.llm_model,
                    "llm_instructions": instruction_set.llm_instructions,
                    "llm_clipboard_text_enabled": instruction_set.llm_clipboard_text_enabled,
                    "llm_clipboard_image_enabled": instruction_set.llm_clipboard_image_enabled,
                    "hotkey": instruction_set.hotkey
                })
                
                data = {
                    "active_set": self.active_set_name or "",
                    "sets": sets_data
                }
            else:
                # Export all sets
                data = self.export_to_dict()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.instruction_sets_file), exist_ok=True)
            
            # Save to file
            with open(self.instruction_sets_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error saving instruction sets: {e}")
            return False
    
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
    
    def create_set(self, name: str, vocabulary: List[str] = None, instructions: List[str] = None, 
                language: Optional[str] = None, model: str = "gpt-4o-transcribe",
                llm_enabled: bool = False, llm_model: str = "gpt-4o", 
                llm_instructions: List[str] = None, llm_clipboard_text_enabled: bool = False,
                llm_clipboard_image_enabled: bool = False, hotkey: str = "") -> bool:
        """
        Create a new instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set.
        vocabulary : List[str], optional
            List of custom vocabulary words, by default None.
        instructions : List[str], optional
            List of system instructions, by default None.
        language : Optional[str], optional
            Language code (e.g., "en", "ja"), or None for auto-detection, by default None.
        model : str, optional
            Model ID to use, by default "gpt-4o-transcribe".
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
            vocabulary=vocabulary or [],
            instructions=instructions or [],
            language=language,
            model=model,
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
                # Get clipboard fields
                llm_clipboard_text_enabled = set_data.get("llm_clipboard_text_enabled", False)
                llm_clipboard_image_enabled = set_data.get("llm_clipboard_image_enabled", False)
                
                self.sets[name] = InstructionSet(
                    name=name,
                    vocabulary=set_data.get("vocabulary", []),
                    instructions=set_data.get("instructions", []),
                    language=set_data.get("language", None),
                    model=set_data.get("model", "gpt-4o-transcribe"),
                    llm_enabled=set_data.get("llm_enabled", False),
                    llm_model=set_data.get("llm_model", "gpt-4o"),
                    llm_instructions=set_data.get("llm_instructions", []),
                    llm_clipboard_text_enabled=llm_clipboard_text_enabled,
                    llm_clipboard_image_enabled=llm_clipboard_image_enabled,
                    hotkey=set_data.get("hotkey", "")
                )
        
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
        sets_data = []
        for name, instruction_set in self.sets.items():
            sets_data.append({
                "name": name,
                "vocabulary": instruction_set.vocabulary,
                "instructions": instruction_set.instructions,
                "language": instruction_set.language,
                "model": instruction_set.model,
                "llm_enabled": instruction_set.llm_enabled,
                "llm_model": instruction_set.llm_model,
                "llm_instructions": instruction_set.llm_instructions,
                "llm_clipboard_text_enabled": instruction_set.llm_clipboard_text_enabled,
                "llm_clipboard_image_enabled": instruction_set.llm_clipboard_image_enabled,
                "hotkey": instruction_set.hotkey
            })
        
        return {
            "active_set": self.active_set_name or "",
            "sets": sets_data
        }
