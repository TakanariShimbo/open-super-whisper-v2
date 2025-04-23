"""
Resource Helper Utilities

This module provides helper functions for managing application resources.
"""

import os
import sys


def getResourcePath(relative_path: str) -> str:
    """
    Get the absolute path to a resource file.
    
    This function resolves the correct path to a resource file, whether
    the application is running from source or is bundled by PyInstaller.
    
    Parameters
    ----------
    relative_path : str
        Path relative to the application root or executable.
        
    Returns
    -------
    str
        Absolute path to the resource.
    """
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    try:
        base_path = sys._MEIPASS  # type: ignore
    except Exception:
        # If not running as a bundled executable, use the script's directory
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    return os.path.join(base_path, relative_path)
