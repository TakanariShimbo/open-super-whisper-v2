"""
Instruction Set Management

This module provides classes for managing custom vocabulary and
system instructions used in the transcription process.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from PyQt6.QtCore import QSettings


@dataclass
class InstructionSet:
    """
    A set of custom vocabulary and instructions for transcription.
    
    This class represents a named collection of vocabulary and instructions
    that can be applied to a transcription request.
    """
    name: str
    vocabulary: List[str]
    instructions: List[str]


class InstructionSetManager:
    """
    Manager for instruction sets.
    
    This class provides methods to create, edit, and manage multiple
    instruction sets, and to select which set is currently active.
    """
    
    def __init__(self, settings: QSettings):
        """
        Initialize the InstructionSetManager.
        
        Parameters
        ----------
        settings : QSettings
            QSettings object to store and retrieve sets.
        """
        self.settings = settings
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
    
    def create_set(self, name: str, vocabulary: List[str] = None, instructions: List[str] = None) -> bool:
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
            instructions=instructions or []
        )
        
        # If this is the first set, make it active
        if len(self.sets) == 1:
            self.active_set_name = name
        
        return True
    
    def update_set(self, name: str, vocabulary: List[str] = None, instructions: List[str] = None) -> bool:
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
            instructions=instruction_set.instructions
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
    
    def save_to_settings(self) -> None:
        """
        Save all instruction sets to settings.
        
        This method serializes all sets to the QSettings object
        provided in the constructor.
        """
        # Save sets count for iteration
        prefix = "InstructionSets"
        self.settings.beginGroup(prefix)
        
        # Remove any existing sets first
        self.settings.remove("")
        
        # Save sets count
        self.settings.setValue("Count", len(self.sets))
        
        # Save active set
        self.settings.setValue("ActiveSet", self.active_set_name or "")
        
        # Save each set
        i = 0
        for name, instruction_set in self.sets.items():
            self.settings.setValue(f"Set{i}/Name", name)
            self.settings.setValue(f"Set{i}/Vocabulary", instruction_set.vocabulary)
            self.settings.setValue(f"Set{i}/Instructions", instruction_set.instructions)
            i += 1
        
        self.settings.endGroup()
        self.settings.sync()
    
    def load_from_settings(self) -> None:
        """
        Load instruction sets from settings.
        
        This method deserializes sets from the QSettings object
        provided in the constructor.
        """
        # Clear existing sets
        self.sets.clear()
        
        # Load sets from settings
        prefix = "InstructionSets"
        self.settings.beginGroup(prefix)
        
        # Get sets count
        count = self.settings.value("Count", 0, int)
        
        # Get active set
        self.active_set_name = self.settings.value("ActiveSet", "")
        
        # Load each set
        for i in range(count):
            name = self.settings.value(f"Set{i}/Name", "")
            vocabulary = self.settings.value(f"Set{i}/Vocabulary", [], list)
            instructions = self.settings.value(f"Set{i}/Instructions", [], list)
            
            self.sets[name] = InstructionSet(name=name, vocabulary=vocabulary, instructions=instructions)
        
        self.settings.endGroup()
        
        # If no sets were loaded, create a default set
        if not self.sets:
            default_name = "Default"
            self.create_set(default_name)
            self.active_set_name = default_name
