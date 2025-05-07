"""
Instruction Manager

This module provides functionality for managing instruction sets
used in speech-to-text and LLM processing.
"""

# Standard library imports
from typing import List, Optional, Dict, Any

# Local application imports
from .instruction_set import InstructionSet


class InstructionManager:
    """
    Manager for instruction sets.
    
    This class provides methods to add, delete, and manage
    instruction sets for speech-to-text and LLM processing.
    """
    
    def __init__(self):
        """
        Initialize the InstructionManager.
        """
        self.sets: Dict[str, InstructionSet] = {}
        
    def add_set(self, instruction_set: InstructionSet) -> bool:
        """
        Add a new instruction set.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The instruction set to add.
            
        Returns
        -------
        bool
            True if set was added, False if a set with the same name already exists.
        """
        if instruction_set.name in self.sets:
            return False
        
        self.sets[instruction_set.name] = instruction_set
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
                
        # delete the set
        del self.sets[name]
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
        instruction_set_dict = self.sets[old_name].to_dict()
        instruction_set_dict["name"] = new_name
        self.add_set(InstructionSet.from_dict(instruction_set_dict))
        
        # Remove old entry
        self.delete_set(old_name)
        
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

    def find_set_by_name(self, name: str) -> Optional[InstructionSet]:
        """
        Find an instruction set by its name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to find.
            
        Returns
        -------
        Optional[InstructionSet]
            The instruction set with the given name, or None if not found.
        """
        return self.sets.get(name)

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
        # Clear existing sets
        self.sets.clear()
        
        # Import sets
        sets_data = data.get("sets", [])
            
        for set_data in sets_data:
            if not isinstance(set_data, dict):
                continue  # Skip invalid entries
                
            name = set_data.get("name", "")
            if name:
                self.sets[name] = InstructionSet.from_dict(set_data)
    
        # If no sets were loaded, create a default set
        if not self.sets:
            self.add_set(InstructionSet(name= "Default"))
    
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
            "sets": sets_data
        }