"""
Instruction Dialog Factory

This module provides a factory for creating instruction dialog instances,
following the factory design pattern to centralize dialog creation logic.
"""

from PyQt6.QtWidgets import QWidget

from ..dialogs.instruction_dialog import InstructionDialog


class InstructionDialogFactory:
    """
    Factory class for creating instruction dialog instances.
    
    This class provides methods to create properly configured instruction
    dialog instances with their controllers and models, following the MVC pattern.
    """
    
    @staticmethod
    def create_dialog(parent: QWidget | None = None) -> InstructionDialog:
        """
        Create an instruction dialog instance.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
            
        Returns
        -------
        InstructionDialog
            The created instruction dialog instance
        """        
        # Create dialog with controller
        dialog = InstructionDialog(parent)

        return dialog
