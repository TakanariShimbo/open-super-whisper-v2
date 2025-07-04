"""
Instruction Sets Manager

This module provides functionality for managing instruction sets
used in speech-to-text and LLM processing.
"""

from typing import Any

from .instruction_set import InstructionSet


class InstructionSetsManager:
    """
    Manager for instruction sets.

    This class provides methods to add, delete, and manage
    instruction sets for speech-to-text and LLM processing.
    """

    def __init__(self) -> None:
        """
        Initialize the InstructionManager.
        """
        self._sets: dict[str, InstructionSet] = {}

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
        if instruction_set.name in self._sets:
            return False

        self._sets[instruction_set.name] = instruction_set
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
        if name not in self._sets:
            return False

        # Don't allow deleting the last set
        if len(self._sets) <= 1:
            return False

        # delete the set
        del self._sets[name]
        return True

    def rename_set(
        self,
        old_name: str,
        new_name: str,
    ) -> bool:
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
        if old_name not in self._sets or new_name in self._sets:
            return False

        # Create a new entry with the same contents but different name
        old_instruction_set_dict = self._sets[old_name].to_dict()
        old_instruction_set_dict["name"] = new_name
        new_instruction_set = InstructionSet.from_dict(data=old_instruction_set_dict)
        self.add_set(instruction_set=new_instruction_set)

        # Remove old entry
        self.delete_set(name=old_name)

        return True

    def get_all_sets(self) -> list[InstructionSet]:
        """
        Get all instruction sets.

        Returns
        -------
        list[InstructionSet]
            List of all instruction sets.
        """
        return list(self._sets.values())

    def find_set_by_name(self, name: str) -> InstructionSet | None:
        """
        Find an instruction set by its name.

        Parameters
        ----------
        name : str
            Name of the instruction set to find.

        Returns
        -------
        InstructionSet | None
            The instruction set with the given name, or None if not found.
        """
        return self._sets.get(name)

    def find_set_by_hotkey(self, hotkey: str) -> InstructionSet | None:
        """
        Find an instruction set by its hotkey.

        Parameters
        ----------
        hotkey : str
            Hotkey string.

        Returns
        -------
        InstructionSet | None
            The instruction set with the given hotkey, or None if not found.
        """
        # Normalize the input hotkey
        normalized_input = self._normalize_hotkey(hotkey)
        
        for instruction_set in self._sets.values():
            # Normalize the stored hotkey for comparison
            normalized_stored = self._normalize_hotkey(instruction_set.hotkey)
            if normalized_stored == normalized_input:
                return instruction_set
        return None
    
    def _normalize_hotkey(self, hotkey: str) -> str:
        """
        Normalize a hotkey string for comparison.
        
        This ensures that hotkeys like "ctrl+alt+1" and "alt+ctrl+1" are treated as equal.
        
        Parameters
        ----------
        hotkey : str
            The hotkey string to normalize.
        
        Returns
        -------
        str
            Normalized hotkey string with modifier keys sorted.
        """
        if not hotkey:
            return ""
        
        # Split the hotkey by '+'
        parts = [part.strip().lower() for part in hotkey.split('+')]
        
        # Define modifier keys in preferred order
        modifier_order = ['ctrl', 'alt', 'shift', 'cmd']
        modifiers = []
        regular_keys = []
        
        for part in parts:
            if part in modifier_order:
                modifiers.append(part)
            else:
                regular_keys.append(part)
        
        # Sort modifiers by their preferred order
        modifiers.sort(key=lambda x: modifier_order.index(x))
        
        # Sort regular keys alphabetically
        regular_keys.sort()
        
        # Combine and return
        normalized_parts = modifiers + regular_keys
        return '+'.join(normalized_parts)

    def import_from_dict(self, data: list[dict[str, Any]]) -> None:
        """
        Import instruction sets from an external list.

        This method loads instruction set configurations from external
        data (e.g., from a JSON file) into the current manager instance.

        Parameters
        ----------
        data : list[dict[str, Any]]
            List containing serialized instruction sets.
        """
        # Clear existing sets
        self._sets.clear()

        # Import sets
        sets_data = data if isinstance(data, list) else []

        for set_data in sets_data:
            if not isinstance(set_data, dict):
                continue  # Skip invalid entries

            name = set_data.get("name", "")
            if name == "":
                continue  # Skip invalid entries

            self.add_set(instruction_set=InstructionSet.from_dict(data=set_data))

    def export_to_dict(self) -> list[dict[str, Any]]:
        """
        Export instruction sets to a list for external serialization.

        This method prepares the current instruction set configuration
        for saving to external storage (e.g., JSON file).

        Returns
        -------
        list[dict[str, Any]]
            List containing serialized instruction sets.
        """
        return [instruction_set.to_dict() for instruction_set in self._sets.values()]
