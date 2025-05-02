"""
Instruction Sets Management

This module provides classes for managing instruction sets,
including vocabulary, system instructions, and LLM settings.
"""

from typing import Dict, List, Optional, Any


class InstructionSet:
    """
    Instruction set with vocabulary, system instructions, and LLM settings.
    
    This class represents a single instruction set, which contains
    vocabulary, system instructions, language settings, model selection,
    and LLM-related settings.
    """
    
    def __init__(self, name: str, vocabulary: List[str] = None, instructions: List[str] = None,
                language: Optional[str] = None, model: str = "gpt-4o-transcribe",
                llm_enabled: bool = False, llm_model: str = "gpt-4o",
                llm_instructions: List[str] = None, llm_clipboard_text_enabled: bool = False,
                llm_clipboard_image_enabled: bool = False, hotkey: str = ""):
        """
        Initialize an InstructionSet.
        
        Parameters
        ----------
        name : str
            Name of the instruction set.
        vocabulary : List[str], optional
            List of custom vocabulary terms, by default None.
        instructions : List[str], optional
            List of system instructions, by default None.
        language : Optional[str], optional
            Language code (e.g., "en", "fr"), by default None (auto-detect).
        model : str, optional
            Whisper model to use, by default "gpt-4o-transcribe".
        llm_enabled : bool, optional
            Whether LLM processing is enabled, by default False.
        llm_model : str, optional
            LLM model to use, by default "gpt-4o".
        llm_instructions : List[str], optional
            List of instructions for LLM, by default None.
        llm_clipboard_text_enabled : bool, optional
            Whether to include clipboard text in LLM input, by default False.
        llm_clipboard_image_enabled : bool, optional
            Whether to include clipboard images in LLM input, by default False.
        hotkey : str, optional
            Hotkey for activating this set, by default empty string.
        """
        self.name = name
        self.vocabulary = vocabulary or []
        self.instructions = instructions or []
        self.language = language
        self.model = model
        self.llm_enabled = llm_enabled
        self.llm_model = llm_model
        self.llm_instructions = llm_instructions or []
        self.llm_clipboard_text_enabled = llm_clipboard_text_enabled
        self.llm_clipboard_image_enabled = llm_clipboard_image_enabled
        self.hotkey = hotkey


class InstructionSetManager:
    """
    Manager for instruction sets.
    
    This class provides methods to create, edit, and manage multiple
    instruction sets. It no longer uses the concept of an "active" set -
    instead, the GUI will select instruction sets from the dropdown or via hotkeys.
    This is a pure Python implementation without GUI dependencies.
    """
    
    def __init__(self):
        """
        Initialize the InstructionSetManager.
        """
        self.sets: Dict[str, InstructionSet] = {}
    
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
            Name of the new instruction set.
        vocabulary : List[str], optional
            List of custom vocabulary terms, by default None.
        instructions : List[str], optional
            List of system instructions, by default None.
        language : Optional[str], optional
            Language code (e.g., "en", "fr"), by default None (auto-detect).
        model : str, optional
            Whisper model to use, by default "gpt-4o-transcribe".
        llm_enabled : bool, optional
            Whether LLM processing is enabled, by default False.
        llm_model : str, optional
            LLM model to use, by default "gpt-4o".
        llm_instructions : List[str], optional
            List of instructions for LLM, by default None.
        llm_clipboard_text_enabled : bool, optional
            Whether to include clipboard text in LLM input, by default False.
        llm_clipboard_image_enabled : bool, optional
            Whether to include clipboard images in LLM input, by default False.
        hotkey : str, optional
            Hotkey for activating this set, by default empty string.
            
        Returns
        -------
        bool
            True if successful, False if name already exists.
            
        Examples
        --------
        >>> manager = InstructionSetManager()
        >>> manager.create_set("Default", vocabulary=["term1", "term2"], 
        ...                   instructions=["Use technical terms"])
        True
        >>> manager.create_set("Default")  # Already exists
        False
        """
        # Check if name already exists
        if name in self.sets:
            return False
        
        # Create set
        self.sets[name] = InstructionSet(
            name=name,
            vocabulary=vocabulary,
            instructions=instructions,
            language=language,
            model=model,
            llm_enabled=llm_enabled,
            llm_model=llm_model,
            llm_instructions=llm_instructions,
            llm_clipboard_text_enabled=llm_clipboard_text_enabled,
            llm_clipboard_image_enabled=llm_clipboard_image_enabled,
            hotkey=hotkey
        )
        
        return True
    
    def update_set(self, name: str, vocabulary: List[str] = None, instructions: List[str] = None,
                 language: Optional[str] = None, model: Optional[str] = None,
                 llm_enabled: Optional[bool] = None, llm_model: Optional[str] = None,
                 llm_instructions: List[str] = None, llm_clipboard_text_enabled: Optional[bool] = None,
                 llm_clipboard_image_enabled: Optional[bool] = None, hotkey: Optional[str] = None) -> bool:
        """
        Update an existing instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to update.
        vocabulary : List[str], optional
            List of custom vocabulary terms, by default None (unchanged).
        instructions : List[str], optional
            List of system instructions, by default None (unchanged).
        language : Optional[str], optional
            Language code, by default None (unchanged).
        model : Optional[str], optional
            Whisper model to use, by default None (unchanged).
        llm_enabled : Optional[bool], optional
            Whether LLM processing is enabled, by default None (unchanged).
        llm_model : Optional[str], optional
            LLM model to use, by default None (unchanged).
        llm_instructions : List[str], optional
            List of instructions for LLM, by default None (unchanged).
        llm_clipboard_text_enabled : Optional[bool], optional
            Whether to include clipboard text in LLM input, by default None (unchanged).
        llm_clipboard_image_enabled : Optional[bool], optional
            Whether to include clipboard images in LLM input, by default None (unchanged).
        hotkey : Optional[str], optional
            Hotkey for activating this set, by default None (unchanged).
            
        Returns
        -------
        bool
            True if successful, False if name doesn't exist.
            
        Examples
        --------
        >>> manager = InstructionSetManager()
        >>> manager.create_set("Default")
        True
        >>> manager.update_set("Default", vocabulary=["new term"])
        True
        >>> manager.update_set("NonExistent")
        False
        """
        # Check if name exists
        if name not in self.sets:
            return False
        
        # Get existing set
        instruction_set = self.sets[name]
        
        # Update only provided fields
        if vocabulary is not None:
            instruction_set.vocabulary = vocabulary
        if instructions is not None:
            instruction_set.instructions = instructions
        if language is not None:
            instruction_set.language = language
        if model is not None:
            instruction_set.model = model
        if llm_enabled is not None:
            instruction_set.llm_enabled = llm_enabled
        if llm_model is not None:
            instruction_set.llm_model = llm_model
        if llm_instructions is not None:
            instruction_set.llm_instructions = llm_instructions
        if llm_clipboard_text_enabled is not None:
            instruction_set.llm_clipboard_text_enabled = llm_clipboard_text_enabled
        if llm_clipboard_image_enabled is not None:
            instruction_set.llm_clipboard_image_enabled = llm_clipboard_image_enabled
        if hotkey is not None:
            instruction_set.hotkey = hotkey
        
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
            True if successful, False if name doesn't exist or it's the last set.
            
        Examples
        --------
        >>> manager = InstructionSetManager()
        >>> manager.create_set("Set1")
        True
        >>> manager.create_set("Set2")
        True
        >>> manager.delete_set("Set1")
        True
        >>> manager.delete_set("Set1")  # Already deleted
        False
        """
        # Check if name exists
        if name not in self.sets:
            return False
        
        # Don't allow deleting the last set
        if len(self.sets) <= 1:
            return False
                
        # Delete the set
        try:
            del self.sets[name]
            return True
        except KeyError:
            # Extra safety in case the key disappeared (this should never happen)
            return False
    
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
            True if successful, False if old_name doesn't exist or new_name already exists.
            
        Examples
        --------
        >>> manager = InstructionSetManager()
        >>> manager.create_set("Old")
        True
        >>> manager.rename_set("Old", "New")
        True
        >>> manager.rename_set("Old", "New")  # Old name no longer exists
        False
        >>> manager.create_set("Another")
        True
        >>> manager.rename_set("New", "Another")  # New name already exists
        False
        """
        # Check if old name exists
        if old_name not in self.sets:
            return False
        
        # Check if new name already exists
        if new_name in self.sets:
            return False
        
        # Get the old instruction set
        instruction_set = self.sets[old_name]
        
        # Create new entry with new name but same data
        self.sets[new_name] = InstructionSet(
            name=new_name,
            vocabulary=instruction_set.vocabulary,
            instructions=instruction_set.instructions,
            language=instruction_set.language,
            model=instruction_set.model,
            llm_enabled=instruction_set.llm_enabled,
            llm_model=instruction_set.llm_model,
            llm_instructions=instruction_set.llm_instructions,
            llm_clipboard_text_enabled=instruction_set.llm_clipboard_text_enabled,
            llm_clipboard_image_enabled=instruction_set.llm_clipboard_image_enabled,
            hotkey=instruction_set.hotkey
        )
        
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
    
    def update_set_hotkey(self, name: str, hotkey: str) -> bool:
        """
        Update the hotkey for an instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to update.
        hotkey : str
            New hotkey for the instruction set.
            
        Returns
        -------
        bool
            True if successful, False if name doesn't exist.
        """
        return self.update_set(name, hotkey=hotkey)
    
    def find_set_by_hotkey(self, hotkey: str) -> Optional[InstructionSet]:
        """
        Find an instruction set by its hotkey.
        
        Parameters
        ----------
        hotkey : str
            Hotkey to search for.
            
        Returns
        -------
        Optional[InstructionSet]
            The instruction set with the given hotkey, or None if not found.
        """
        for instruction_set in self.sets.values():
            if instruction_set.hotkey == hotkey:
                return instruction_set
        return None
    
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
    
    def import_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Import instruction sets from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing serialized instruction sets.
        """
        # Validate input data
        if not isinstance(data, dict):
            return
        
        # Clear existing sets
        self.sets.clear()
        
        # Import sets
        sets_data = data.get("sets", [])
        if not isinstance(sets_data, list):
            # If "sets" is not a list, create a default set
            self.create_set("Default")
            return
        
        # Process each set
        for set_data in sets_data:
            if isinstance(set_data, dict) and "name" in set_data:
                # Create set from dict data
                self.create_set(
                    name=set_data.get("name", ""),
                    vocabulary=set_data.get("vocabulary", []),
                    instructions=set_data.get("instructions", []),
                    language=set_data.get("language"),
                    model=set_data.get("model", "gpt-4o-transcribe"),
                    llm_enabled=set_data.get("llm_enabled", False),
                    llm_model=set_data.get("llm_model", "gpt-4o"),
                    llm_instructions=set_data.get("llm_instructions", []),
                    llm_clipboard_text_enabled=set_data.get("llm_clipboard_text_enabled", False),
                    llm_clipboard_image_enabled=set_data.get("llm_clipboard_image_enabled", False),
                    hotkey=set_data.get("hotkey", "")
                )
        
        # If no sets were loaded, create a default set
        if not self.sets:
            default_name = "Default"
            self.create_set(default_name)
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export instruction sets to a dictionary.
        
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
            "sets": sets_data
        }
