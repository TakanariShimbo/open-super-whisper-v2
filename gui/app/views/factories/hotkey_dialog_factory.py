"""
Hotkey Dialog Factory

This module provides a factory for creating hotkey dialog instances,
following the factory design pattern to centralize dialog creation logic.
"""

from ..dialogs.hotkey_dialog import HotkeyDialog
from ...models.hotkey_model import HotkeyModel
from ...models.dialogs.instruction_dialog_model import InstructionDialogModel


class HotkeyDialogFactory:
    """
    Factory class for creating hotkey dialog instances.
    
    This class provides methods to create properly configured hotkey
    dialog instances with their controllers, following the MVC pattern.
    """
    
    @staticmethod
    def _create_dialog(
        parent=None, 
        current_hotkey: str = "",
        hotkey_manager: HotkeyModel | None = None,
        conflict_checker=None,
        instruction_dialog_model=None
    ) -> HotkeyDialog:
        """
        Create a generic hotkey dialog instance.
        
        This method creates a new hotkey dialog with its controller,
        properly configured and ready to use.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
        current_hotkey : str, optional
            Current hotkey value, by default ""
        hotkey_manager : HotkeyModel | None, optional
            Hotkey manager for handling system-wide hotkeys, by default None
        conflict_checker : callable, optional
            Function to check for hotkey conflicts, by default None
        instruction_dialog_model : InstructionDialogModel | None, optional
            For backward compatibility - model containing instruction sets for conflict checking
            
        Returns
        -------
        HotkeyDialog
            The created hotkey dialog instance
        """
        # Create a hotkey dialog with the controller
        dialog = HotkeyDialog(
            parent=parent,
            current_hotkey=current_hotkey,
            hotkey_manager=hotkey_manager,
            conflict_checker=conflict_checker,
            instruction_dialog_model=instruction_dialog_model
        )
        
        return dialog
    
    @classmethod
    def create_instruction_set_dialog(
        cls,
        parent=None,
        current_hotkey: str = "",
        hotkey_manager: HotkeyModel | None = None,
        instruction_model: InstructionDialogModel | None = None
    ) -> HotkeyDialog:
        """
        Create a hotkey dialog for instruction sets.
        
        This method creates a dialog specifically for setting hotkeys
        for instruction sets, with appropriate conflict checking.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
        current_hotkey : str, optional
            Current hotkey value, by default ""
        hotkey_manager : HotkeyModel | None, optional
            Hotkey manager for handling system-wide hotkeys, by default None
        instruction_model : InstructionDialogModel | None, optional
            Model containing instruction sets for conflict checking, by default None
            
        Returns
        -------
        HotkeyDialog
            The created hotkey dialog instance
        """
        # Create conflict checker function if instruction model is provided
        conflict_checker = None
        if instruction_model and hasattr(instruction_model, 'get_set_by_hotkey'):
            def check_hotkey_conflict(hotkey: str) -> str | None:
                conflicting_set = instruction_model.get_set_by_hotkey(hotkey)
                if conflicting_set:
                    return f"The hotkey '{hotkey}' is already used by instruction set '{conflicting_set.name}'."
                return None
            
            conflict_checker = check_hotkey_conflict
        
        # Create dialog with conflict checker
        return cls._create_dialog(
            parent=parent,
            current_hotkey=current_hotkey,
            hotkey_manager=hotkey_manager,
            conflict_checker=conflict_checker,
            instruction_dialog_model=instruction_model
        )
    
    @classmethod
    def create_global_action_dialog(
        cls,
        parent=None,
        current_hotkey: str = "",
        hotkey_manager: HotkeyModel | None = None,
        action_name: str = "",
        existing_hotkeys: list[str] = None
    ) -> HotkeyDialog:
        """
        Create a hotkey dialog for global actions.
        
        This method creates a dialog specifically for setting hotkeys
        for global actions, with appropriate conflict checking against
        a list of existing hotkeys.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
        current_hotkey : str, optional
            Current hotkey value, by default ""
        hotkey_manager : HotkeyModel | None, optional
            Hotkey manager for handling system-wide hotkeys, by default None
        action_name : str, optional
            Name of the action for display in conflict messages, by default ""
        existing_hotkeys : list[str], optional
            List of existing hotkeys to check for conflicts, by default None
            
        Returns
        -------
        HotkeyDialog
            The created hotkey dialog instance
        """
        # Create conflict checker function if existing hotkeys is provided
        conflict_checker = None
        if existing_hotkeys:
            def check_hotkey_conflict(hotkey: str) -> str | None:
                if hotkey in existing_hotkeys and hotkey != current_hotkey:
                    return f"The hotkey '{hotkey}' is already in use by another action."
                return None
            
            conflict_checker = check_hotkey_conflict
        
        # Create dialog with conflict checker
        return cls._create_dialog(
            parent=parent,
            current_hotkey=current_hotkey,
            hotkey_manager=hotkey_manager,
            conflict_checker=conflict_checker,
            instruction_dialog_model=None
        )
