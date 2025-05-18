"""
Instruction Dialog Factory

This module provides a factory for creating instruction dialog instances,
following the factory design pattern to centralize dialog creation logic.
"""

from ..dialogs.instruction_dialog import InstructionDialog
from ...controllers.dialogs.instruction_dialog_controller import InstructionDialogController
from ...models.dialogs.instruction_dialog_model import InstructionDialogModel


class InstructionDialogFactory:
    """
    Factory class for creating instruction dialog instances.
    
    This class provides methods to create properly configured instruction
    dialog instances with their controllers and models, following the MVC pattern.
    """
    
    @staticmethod
    def create_dialog(parent=None, parent_controller=None) -> InstructionDialog:
        """
        Create an instruction dialog instance.
        
        This method creates a new instruction dialog with its controller and model,
        properly configured and ready to use.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
        parent_controller : QObject, optional
            Parent controller for dependency injection, by default None
            
        Returns
        -------
        InstructionDialog
            The created instruction dialog instance
        """        
        # Create model
        model = InstructionDialogModel()
        
        # Create controller with model
        controller = InstructionDialogController(model, parent_controller)
        
        # Create dialog with controller
        dialog = InstructionDialog(controller, parent)
        
        return dialog
