"""
Instruction Set Management

This module provides classes for managing custom vocabulary and
system instructions used in the transcription process.
This is the core, non-GUI dependent implementation.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class InstructionSet:
    """
    A set of custom vocabulary, instructions, language, and model for transcription.
    
    This class represents a named collection of settings that can be applied
    to a transcription request, including custom vocabulary, system instructions,
    preferred language, and transcription model.
    """
    name: str
    vocabulary: List[str] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    language: Optional[str] = None  # Language code (e.g., "en", "ja"), None for auto-detection
    model: str = "whisper-1"  # Default model ID


class InstructionSetManager:
    """
    Manager for instruction sets.
    
    This class provides methods to create, edit, and manage multiple
    instruction sets, and to select which set is currently active.
    This is a pure Python implementation without GUI dependencies.
    """
    
    def __init__(self):
        """
        Initialize the InstructionSetManager.
        """
        self.sets: Dict[str, InstructionSet] = {}
        self.active_set_name: Optional[str] = None
    
    @property
    def active_set(self) -> Optional[InstructionSet]:
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
                language: Optional[str] = None, model: str = "whisper-1") -> bool:
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
            Whisper model ID to use, by default "whisper-1".
            
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
            model=model
        )
        
        # If this is the first set, make it active
        if len(self.sets) == 1:
            self.active_set_name = name
        
        return True
    
    def update_set(self, name: str, vocabulary: List[str] = None, instructions: List[str] = None,
                 language: Optional[str] = None, model: Optional[str] = None) -> bool:
        """
        Update an existing instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to update.
        vocabulary : List[str], optional
            New vocabulary list, by default None (unchanged).
        instructions : List[str], optional
            New instructions list, by default None (unchanged).
        language : Optional[str], optional
            Language code (e.g., "en", "ja"), by default None (unchanged).
        model : str, optional
            Whisper model ID to use, by default None (unchanged).
            
        Returns
        -------
        bool
            True if set was updated, False if name doesn't exist.
        """
        if name not in self.sets:
            return False
        
        if vocabulary is not None:
            self.sets[name].vocabulary = vocabulary
        
        if instructions is not None:
            self.sets[name].instructions = instructions
            
        if language is not None:
            self.sets[name].language = language
            
        if model is not None:
            self.sets[name].model = model
        
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
            True if set was deleted, False if name doesn't exist.
        """
        if name not in self.sets:
            return False
        
        # Don't allow deleting the last set
        if len(self.sets) <= 1:
            return False
        
        # If deleting the active set, select another one
        if name == self.active_set_name:
            for other_name in self.sets:
                if other_name != name:
                    self.active_set_name = other_name
                    break
        
        del self.sets[name]
        return True
    
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
            vocabulary=instruction_set.vocabulary,
            instructions=instruction_set.instructions,
            language=instruction_set.language,
            model=instruction_set.model
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
    
    def get_active_vocabulary(self) -> List[str]:
        """
        Get vocabulary from the active set.
        
        Returns
        -------
        List[str]
            List of vocabulary items from the active set,
            or an empty list if no active set.
        """
        if not self.active_set:
            return []
        return self.active_set.vocabulary
    
    def get_active_instructions(self) -> List[str]:
        """
        Get instructions from the active set.
        
        Returns
        -------
        List[str]
            List of instructions from the active set,
            or an empty list if no active set.
        """
        if not self.active_set:
            return []
        return self.active_set.instructions
        
    def get_active_language(self) -> Optional[str]:
        """
        Get language setting from the active set.
        
        Returns
        -------
        Optional[str]
            Language code from the active set,
            or None if no active set or no language specified.
        """
        if not self.active_set:
            return None
        return self.active_set.language
        
    def get_active_model(self) -> str:
        """
        Get model setting from the active set.
        
        Returns
        -------
        str
            Model ID from the active set,
            or "whisper-1" if no active set.
        """
        if not self.active_set:
            return "whisper-1"
        return self.active_set.model
    
    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load instruction sets from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing serialized instruction sets.
        """
        # Clear existing sets
        self.sets.clear()
        
        # Load active set name
        self.active_set_name = data.get("active_set", "")
        
        # Load sets
        sets_data = data.get("sets", [])
        for set_data in sets_data:
            name = set_data.get("name", "")
            if name:
                self.sets[name] = InstructionSet(
                    name=name,
                    vocabulary=set_data.get("vocabulary", []),
                    instructions=set_data.get("instructions", []),
                    language=set_data.get("language", None),
                    model=set_data.get("model", "whisper-1")
                )
        
        # If no sets were loaded and active_set_name is empty, create a default set
        if not self.sets:
            default_name = "Default"
            self.create_set(default_name)
            self.active_set_name = default_name
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert instruction sets to a dictionary for serialization.
        
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
                "model": instruction_set.model
            })
        
        return {
            "active_set": self.active_set_name or "",
            "sets": sets_data
        }
