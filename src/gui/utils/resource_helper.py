"""
Resource Helper Utilities

This module provides utility functions for accessing resources
like asset files in a consistent way regardless of how the application
is run (directly or as a compiled package).
"""

import os
import sys


def getResourcePath(relative_path: str) -> str:
    """
    Get the absolute path to a resource file.
    
    This function handles the path resolution for resources whether the
    application is running from source or from a bundled package.
    
    Parameters
    ----------
    relative_path : str
        The path to the resource, relative to the application's base directory.
        
    Returns
    -------
    str
        The absolute path to the resource.
    """
    # If the application is frozen (compiled with PyInstaller)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # We're running in development mode, use the main script's directory
        base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
    
    # Normalize path format for the current OS
    return os.path.normpath(os.path.join(base_path, relative_path))
