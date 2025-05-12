"""
Status Indicator Factory

This module provides a factory for creating status indicator instances,
following the factory design pattern to centralize view creation logic.
"""

from ..widgets.status_indicator import StatusIndicatorWindow


class StatusIndicatorFactory:
    """
    Factory class for creating status indicator instances.
    
    This class provides methods to create properly configured status indicator
    view instances, following the MVC pattern.
    """
    
    @staticmethod
    def create_status_indicator(parent=None) -> StatusIndicatorWindow:
        """
        Create a status indicator instance.
        
        This method creates a new status indicator view properly configured
        and ready to use. The controller and model are not created here,
        as they are created and connected by the AppController.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the status indicator, by default None
            
        Returns
        -------
        StatusIndicatorWindow
            The created status indicator view
        """
        # Create view (controller will be created by the caller)
        view = StatusIndicatorWindow(parent)
        
        return view
